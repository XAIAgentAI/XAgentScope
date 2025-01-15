# -*- coding: utf-8 -*-
"""run web ui"""
import argparse
import os
import sys
import threading
import time
from collections import defaultdict
from typing import Optional, Callable, Dict, Any, List
import traceback
import socketio
from loguru import logger
import gradio.components as gr_components
import gradio.routes as gr_routes
import gradio.blocks as gr_blocks

try:
    import gradio as gr
except ImportError as e:
    print(f"Failed to import gradio: {e}", file=sys.stderr)
    print("Please install the [full] version of AgentScope", file=sys.stderr)
    sys.exit(1)

# modelscope_studio import removed - not used
# Fallback to built-in Gradio components

from agentscope.web.gradio.utils import (
    send_player_input,
    get_chat_msg,
    SYS_MSG_PREFIX,
    ResetException,
    check_uuid,
    send_msg,
    generate_image_from_name,
    audio2text,
    send_reset_msg,
    thread_local_data,
    cycle_dots,
)
from agentscope.web.gradio.constants import _SPEAK

MAX_NUM_DISPLAY_MSG = 20
FAIL_COUNT_DOWN = 30


def init_uid_list() -> list:
    """Initialize an empty list for storing user IDs."""
    return []


glb_history_dict = defaultdict(init_uid_list)
glb_doing_signal_dict = defaultdict(init_uid_list)
glb_signed_user = []


def reset_glb_var(uid: str) -> None:
    """Reset global variables for a given user ID."""
    global glb_history_dict
    global glb_doing_signal_dict
    glb_history_dict[uid] = init_uid_list()
    glb_doing_signal_dict[uid] = init_uid_list()


def get_chat(uid: str) -> list[list]:
    """Retrieve chat messages for a given user ID."""
    uid = check_uuid(uid)
    global glb_history_dict
    global glb_doing_signal_dict

    line = get_chat_msg(uid=uid)
    # TODO: Optimize the display effect, currently there is a problem of
    #  output display jumping
    if line:
        if line[1] and line[1]["text"] == _SPEAK:
            line[1]["text"] = ""
            glb_doing_signal_dict[uid] = line
        else:
            glb_history_dict[uid] += [line]
            glb_doing_signal_dict[uid] = []
    dial_msg = []
    for line in glb_history_dict[uid]:
        _, msg = line
        if isinstance(msg, dict):
            dial_msg.append(line)
        else:
            # User chat, format: (msg, None)
            dial_msg.append(line)
    if glb_doing_signal_dict[uid]:
        if glb_doing_signal_dict[uid][1]:
            text = cycle_dots(glb_doing_signal_dict[uid][1]["text"])
            glb_doing_signal_dict[uid][1]["text"] = text
            glb_doing_signal_dict[uid][1]["id"] = str(time.time())
            glb_doing_signal_dict[uid][1]["flushing"] = False

        dial_msg.append(glb_doing_signal_dict[uid])
    return dial_msg[-MAX_NUM_DISPLAY_MSG:]


def send_audio(audio_term: str, uid: str) -> None:
    """Convert audio input to text and send as a chat message."""
    uid = check_uuid(uid)
    content = audio2text(audio_path=audio_term)
    send_player_input(content, uid=uid)
    msg = f"""{content}
    <audio src="{audio_term}"></audio>"""
    send_msg(msg, is_player=True, role="Me", uid=uid, avatar=None)


def send_image(image_term: str, uid: str) -> None:
    """Send an image as a chat message."""
    uid = check_uuid(uid)
    send_player_input(image_term, uid=uid)

    msg = f"""<img src="{image_term}"></img>"""
    avatar = generate_image_from_name("Me")
    send_msg(msg, is_player=True, role="Me", uid=uid, avatar=avatar)


def send_message(msg: str, uid: str) -> str:
    """Send a generic message to the player."""
    uid = check_uuid(uid)
    send_player_input(msg, uid=uid)
    avatar = generate_image_from_name("Me")
    send_msg(msg, is_player=True, role="Me", uid=uid, avatar=avatar)
    return ""


def fn_choice(data: gr_routes.EventData, uid: str) -> None:
    """Handle a selection event from the chatbot interface."""
    uid = check_uuid(uid)
    # pylint: disable=protected-access
    send_player_input(data._data["value"], uid=uid)


def import_function_from_path(
    module_path: str,
    function_name: str,
    module_name: Optional[str] = None,
) -> Callable:
    """Import a function from the given module path."""
    import importlib.util

    script_dir = os.path.dirname(os.path.abspath(module_path))

    # Temporarily add a script directory to sys.path
    original_sys_path = sys.path[:]
    sys.path.insert(0, script_dir)

    try:
        # If a module name is not provided, you can use the filename (
        # without extension) as the module name
        if module_name is None:
            module_name = os.path.splitext(os.path.basename(module_path))[0]
        # Creating module specifications and loading modules
        spec = importlib.util.spec_from_file_location(
            module_name,
            module_path,
        )
        if spec is not None:
            module = importlib.util.module_from_spec(spec)
            if spec.loader is not None:
                spec.loader.exec_module(module)
                # Getting a function from a module
                function = getattr(module, function_name)
            else:
                raise ImportError("Module loader is None")
        else:
            raise ImportError(
                f"Could not find module spec for {module_name} at"
                f" {module_path}",
            )
    except AttributeError as exc:
        raise AttributeError(
            f"The module '{module_name}' does not have a function named '"
            f"{function_name}'. Please put your code in the main function, "
            f"read README.md for details.",
        ) from exc
    finally:
        # Restore the original sys.path
        sys.path = original_sys_path

    return function


# pylint: disable=too-many-statements
def test_model(
    model_type: str,
    config_name: str,
    model_input: str,
    auth_token: Optional[str] = None,
    stream: bool = True,
) -> tuple[Optional[str], Optional[List[str]]]:
    """Test a model through the API endpoint with streaming support.

    Args:
        model_type: Type of model to test ("degpt" or "superimage")
        config_name: Name of the model configuration
        model_input: Input text or prompt
        auth_token: Authentication token (required for Superimage)
        stream: Enable streaming updates (default: True)

    Returns:
        tuple[Optional[str], Optional[List[str]]]: A tuple containing:
            - text_output: Generated text for DeGPT or error message
            - image_urls: List of image URLs for Superimage
    """
    import requests
    from requests.exceptions import RequestException

    def handle_error(msg: str) -> tuple[str, None]:
        """Log error and return formatted error message."""
        logger.error(msg)
        return f"Error: {msg}", None

    # Validate inputs and prepare payload
    if not all([model_type, config_name, model_input]):
        return handle_error("Missing required fields")

    if model_type == "superimage" and not auth_token:
        return handle_error("Auth token is required for Superimage model")

    payload = {
        "model_type": model_type,
        "config_name": config_name,
        "input": model_input,
        "parameters": {"auth_token": auth_token} if auth_token else {},
        "stream": stream,
    }

    try:
        response = requests.post(
            "http://localhost:5000/api/models/test",
            json=payload,
            timeout=30,
        )
        response.raise_for_status()
        result = response.json()

        if result["status"] != "success":
            return handle_error(result.get("message", "Unknown error"))

        output = result["result"]
        return output.get("text"), output.get("image_urls", [])

    except (RequestException, ValueError, Exception) as error:
        return handle_error(f"{error.__class__.__name__} - {str(error)}")


def run_app() -> None:
    """Entry point for the web UI application."""
    assert gr is not None, "Please install [full] version of AgentScope."

    def update_auth_token_visibility(model_type: str) -> dict:
        """Update visibility of auth token input based on model type.

        Args:
            model_type: The selected model type

        Returns:
            dict: Visibility update for auth token input
        """
        return {"visible": model_type == "superimage"}

    def update_output_visibility(model_type: str) -> tuple[dict, dict]:
        """Update visibility of output components based on model type.

        Args:
            model_type: The selected model type

        Returns:
            tuple[dict, dict]: Updates for text/image output visibility
        """
        is_degpt = model_type == "degpt"
        return (
            {
                "visible": True,
                "value": "" if is_degpt else "Image generation mode active",
            },
            {
                "visible": not is_degpt,
                "value": None,
            },  # Clear gallery when hidden
        )

    parser = argparse.ArgumentParser()
    parser.add_argument("script", type=str, help="Script file to run")
    args = parser.parse_args()

    # Make sure script_path is an absolute path
    script_path = os.path.abspath(args.script)

    # Get the directory where the script is located
    script_dir = os.path.dirname(script_path)
    # Save the current working directory
    # Change the current working directory to the directory where
    os.chdir(script_dir)

    def start_game(uid: str) -> None:
        """Start the main game loop."""
        thread_local_data.uid = uid
        if script_path.endswith(".py"):
            main = import_function_from_path(script_path, "main")
        elif script_path.endswith(".json"):
            from agentscope.web.workstation.workflow import (
                start_workflow,
                load_config,
            )

            config = load_config(script_path)
            main = lambda: start_workflow(config)
        else:
            raise ValueError(f"Unrecognized file formats: {script_path}")

        while True:
            try:
                main()
            except ResetException:
                print(f"Reset Successfully：{uid} ")
            except Exception as e_game:
                trace_info = "".join(
                    traceback.TracebackException.from_exception(
                        e_game,
                    ).format(),
                )
                for i in range(FAIL_COUNT_DOWN, 0, -1):
                    send_msg(
                        f"{SYS_MSG_PREFIX} error {trace_info}, reboot "
                        f"in {i} seconds",
                        uid=uid,
                    )
                    time.sleep(1)
            reset_glb_var(uid)

    def check_for_new_session(uid: str) -> None:
        """
        Check for a new user session and start a game thread if necessary.
        """
        uid = check_uuid(uid)
        if uid not in glb_signed_user:
            glb_signed_user.append(uid)
            print("==========Signed User==========")
            print(f"Total number of users: {len(glb_signed_user)}")
            run_thread = threading.Thread(
                target=start_game,
                args=(uid,),
            )
            run_thread.start()

    with gr_blocks.Blocks() as demo:
        warning_html_code = """
                        <div class="hint" style="text-align:
                        center;background-color: rgba(255, 255, 0, 0.15);
                        padding: 10px; margin: 10px; border-radius: 5px;
                        border: 1px solid #ffcc00;">
                        <p>If you want to start over, please click the
                        <strong>reset</strong>
                        button and <strong>refresh</strong> the page</p>
                        </div>
                        """
        gr_components.HTML(warning_html_code)
        uuid = gr_components.Textbox(label="modelscope_uuid", visible=False)

        with gr_blocks.Row():
            chatbot = gr_components.Chatbot(
                label="Dialog",
                show_label=False,
                bubble_full_width=False,
                visible=True,
            )

        with gr_blocks.Column():
            user_chat_input = gr_components.Textbox(
                label="user_chat_input",
                placeholder="Say something here",
                show_label=False,
            )
            send_button = gr_components.Button(value="📣Send")
        with gr_blocks.Row():
            with gr_blocks.Tabs():
                with gr_blocks.Tab("Audio input"):
                    audio_term = gr_components.Audio(
                        visible=True,
                        type="filepath",
                        format="wav",
                    )
                    submit_audio_button = gr_components.Button(
                        value="Send Audio",
                    )
                with gr_blocks.Tab("Image input"):
                    image_term = gr_components.Image(
                        visible=True,
                        height=300,
                        interactive=True,
                        type="filepath",
                    )
                    submit_image_button = gr_components.Button(
                        value="Send Image",
                    )
                # Model Testing Panel
                with gr_blocks.Tab("Model Testing"):
                    with gr_blocks.Row():
                        model_type = gr_components.Dropdown(
                            choices=["degpt", "superimage"],
                            label="Model Type",
                            value="degpt",
                            interactive=True,
                        )
                        config_name = gr_components.Textbox(
                            label="Config Name",
                            placeholder="Enter model config name",
                            interactive=True,
                        )

                    model_input = gr_components.Textbox(
                        label="Input",
                        placeholder=(
                            "Enter text for DeGPT or image prompt "
                            "for Superimage"
                        ),
                        interactive=True,
                        lines=3,
                    )

                    with gr_blocks.Row():
                        auth_token = gr_components.Textbox(
                            label="Auth Token (required for Superimage)",
                            placeholder="Enter auth token",
                            visible=False,
                            interactive=True,
                            type="password",
                        )

                    test_button = gr_components.Button(
                        value="Test Model",
                        variant="primary",
                    )

                    with gr_blocks.Row():
                        output_text = gr_components.Textbox(
                            label="Model Output (Text)",
                            interactive=False,
                            lines=5,
                        )
                        output_gallery = gr_components.Gallery(
                            label="Model Output (Images)",
                            visible=False,
                            columns=2,
                            rows=2,
                            height=400,
                        )

            # Connect UI events
            model_type.change(
                fn=update_auth_token_visibility,
                inputs=[model_type],
                outputs=[auth_token],
            )

            model_type.change(
                fn=update_output_visibility,
                inputs=[model_type],
                outputs=[output_text, output_gallery],
            )

            # Initialize SocketIO for streaming updates
            sio = socketio.Client()

            def setup_socket_handlers() -> None:
                """Set up SocketIO event handlers for model testing."""

                @sio.on("connect", namespace="/model_test")
                def on_connect() -> None:
                    """Handle connection to model test namespace."""
                    logger.info("Connected to model test namespace")

                @sio.on("disconnect", namespace="/model_test")
                def on_disconnect() -> None:
                    """Handle disconnection from model test namespace."""
                    logger.info("Disconnected from model test namespace")

                @sio.on("model_test_update", namespace="/model_test")
                def handle_model_update(data: Dict[str, Any]) -> None:
                    """Handle model test updates from server.

                    Args:
                        data: Server update data with type and payload info
                    """
                    if data.get("type") == "text":
                        # Update text output with new chunk
                        if hasattr(output_text, "value"):
                            current = output_text.value or ""
                            output_text.value = current + data.get("chunk", "")
                    elif data.get("type") == "image":
                        if data.get("status") == "generating":
                            if hasattr(output_text, "value"):
                                output_text.value = "Generating image..."
                        elif data.get("status") == "complete":
                            if hasattr(output_text, "value"):
                                output_text.value = (
                                    "Image generation complete!"
                                )
                    elif data.get("type") == "error":
                        if hasattr(output_text, "value"):
                            output_text.value = (
                                f"Error: {data.get('error', 'Unknown error')}"
                            )

            setup_socket_handlers()

            try:
                if not sio.connected:
                    sio.connect(
                        "http://localhost:5000",
                        namespaces=["/model_test"],
                    )
                    logger.info("Connected to SocketIO server")
            except Exception as e_socket:
                logger.error(f"Failed to connect to SocketIO: {e_socket}")
                setattr(
                    output_text,
                    "value",
                    "Warning: Real-time updates unavailable",
                )

            test_button.click(
                fn=test_model,
                inputs=[
                    model_type,
                    config_name,
                    model_input,
                    auth_token,
                ],
                outputs=[
                    output_text,
                    output_gallery,
                ],
            )

        with gr_blocks.Column():
            reset_button = gr_components.Button(value="Reset")

        # submit message
        send_button.click(
            send_message,
            [user_chat_input, uuid],
            user_chat_input,
        )
        user_chat_input.submit(
            send_message,
            [user_chat_input, uuid],
            user_chat_input,
        )

        submit_audio_button.click(
            send_audio,
            inputs=[audio_term, uuid],
            outputs=[audio_term],
        )

        submit_image_button.click(
            send_image,
            inputs=[image_term, uuid],
            outputs=[image_term],
        )

        reset_button.click(send_reset_msg, inputs=[uuid])

        # Replace custom() with select() for Gradio 4.x compatibility
        chatbot.select(fn=fn_choice, inputs=[uuid])

        # Load initial session and start chat updates
        demo.load(
            fn=check_for_new_session,
            inputs=[uuid],
            every=0.5,
        )

        demo.load(
            fn=get_chat,
            inputs=[uuid],
            outputs=[chatbot],
            every=0.5,
        )

    demo.queue()
    demo.launch()


if __name__ == "__main__":
    run_app()
