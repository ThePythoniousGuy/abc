import asyncio
import subprocess
import time

input_file = "input.mp4"
output_file = "output.mp4"

# Define FFmpeg command to convert video to 30fps
command = ['ffmpeg', '-i', input_file, '-r', '30', '-filter:v', 'setpts=1.0*PTS', output_file]

async def run_ffmpeg_command(command):
    # Create a subprocess to run the FFmpeg command
    s = time.time()
    process = await asyncio.create_subprocess_exec(
        *command,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE
    )
    
    # Wait for the subprocess to complete and capture its output
    stdout, stderr = await process.communicate()
    
    e = time.time()
    
    print(f"Took: {(e-s)*1000:.3f} ms")
    
    # Print the subprocess output
    
    #print(stdout.decode())
    #print(stderr.decode())

# Run the FFmpeg command asynchronously


async def main():
    command = ['ffmpeg', '-i', input_file, '-r', '30', '-filter:v', 'setpts=1.0*PTS']
    
    a = []
    for i in range(1, 3):
        print(i)
        com = command.copy()+[f"output{i}.mp4"]
        a.append(run_ffmpeg_command(com))
    
    await asyncio.gather(*a)
        

asyncio.run(main())
