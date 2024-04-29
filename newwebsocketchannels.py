import asyncio
import cv2
import numpy as np
import keyboard
import websockets
import json
import  time

async def receive_video_stream():
    while True:
        try:
            async with websockets.connect("ws://10.13.0.248:8001") as websocket:
                print("Connected to video streaming endpoint")
                while True:
                    frame_data = await websocket.recv()
                    # Decode frame data
                    nparr = np.frombuffer(frame_data, np.uint8)
                    frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

                    # Display the frame
                    cv2.imshow('Video Stream', frame)
                    cv2.waitKey(1)

                    # Check for keyboard commands
                    if keyboard.is_pressed('q'):
                        break

        except Exception as e:
            print(f"Error: {e}")
            print("Attempting to reconnect...")
            await asyncio.sleep(3)  # Wait for 3 seconds before attempting to reconnect

def send_commands():
    async def send_messages():
        while True:
            try:
                async with websockets.connect("ws://10.13.0.210:8000") as websocket:
                    print("Connected to WebSocket server")
                    last_press_time = 0
                    delay = 0.2  # Delay in seconds between key press events
                    while True:
                        message = {
                            "motor": "stop",
                            "servo": "center"
                        }

                        # Check for key presses
                        if keyboard.is_pressed('w'):
                            message["motor"] = "forward"
                        elif keyboard.is_pressed('s'):
                            message["motor"] = "backward"

                        if keyboard.is_pressed('a'):
                            message["servo"] = "left"
                        elif keyboard.is_pressed('d'):
                            message["servo"] = "right"

                        # Convert message dictionary to JSON string
                        message_json = json.dumps(message)

                        # Send the message
                        await websocket.send(message_json)

                        # Add a delay before sending the next message
                        await asyncio.sleep(0.1)  # Adjust the delay time as needed

                        current_time = time.time()
                        if current_time - last_press_time >= delay:
                            last_press_time = current_time

            except Exception as e:
                print(f"Error: {e}")
                print("Attempting to reconnect...")
                await asyncio.sleep(3)  # Wait for 3 seconds before attempting to reconnect

    asyncio.run(send_messages())

async def main():
    task1 = asyncio.create_task(receive_video_stream())
    task2 = asyncio.create_task(send_commands())
    await asyncio.gather(task1, task2)

if __name__ == "__main__":
    asyncio.run(main())
