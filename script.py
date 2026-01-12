from moviepy.editor import VideoFileClip

# Load the video
video = VideoFileClip("video.mp4")

# Extract audio
video.audio.write_audiofile("output_audio.mp3")

# Extract video without audio
video.without_audio().write_videofile("output_video.mp4", codec="libx264")
