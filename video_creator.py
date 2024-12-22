import os
import glob
from moviepy.editor import ImageClip, AudioFileClip, concatenate_videoclips

def create_clip(img_path):
    # 创建图片剪辑
    clip = ImageClip(img_path, duration=2)
    
    # 获取原始尺寸
    w, h = clip.size
    
    # 定义缩放函数 - 从100%线性变化到120%
    def zoom_func(t):
        """t: 0->2秒, 返回值: [原始宽度,原始高度] -> [放大后宽度,放大后高度]"""
        scale = 1.0 + 0.2 * (t / 2.0)  # 从1.0变化到1.2
        new_w = int(w * scale)
        new_h = int(h * scale)
        return [new_w, new_h]
    
    # 设置居中并添加缩放动画
    clip = (clip
            .set_position('center')  # 确保居中显示
            .resize(zoom_func))      # 添加缩放动画
    
    return clip

def process_batch(image_files, audio_clip, batch_number, output_path):
    print(f"\n处理第 {batch_number} 批图片 ({len(image_files)} 张)")
    
    # 创建视频片段
    clips = []
    for img in image_files:
        print(f"处理图片: {os.path.basename(img)}")
        try:
            clip = create_clip(img)
            clips.append(clip)
        except Exception as e:
            print(f"处理图片 {img} 时出错: {str(e)}")
            continue
    
    if not clips:
        raise Exception("没有成功处理任何图片")
    
    # 合并视频片段
    final_clip = concatenate_videoclips(clips, method="compose")
    
    # 直接从音频开头截取所需长度
    if audio_clip.duration >= final_clip.duration:
        batch_audio = audio_clip.subclip(0, final_clip.duration)
        final_clip = final_clip.set_audio(batch_audio)
    
    # 生成输出文件
    output_file = os.path.join(output_path, f"video_batch_{batch_number}.mp4")
    print(f"生成视频: {output_file}")
    
    # 写入视频文件
    final_clip.write_videofile(
        output_file,
        fps=24,
        codec='libx264',
        audio_codec='aac',
        bitrate='4000k',
        threads=2,
        logger=None
    )
    
    # 清理资源
    final_clip.close()
    for clip in clips:
        clip.close()
    
    print(f"第 {batch_number} 批处理完成")

def create_videos_from_images(image_dir, audio_path, output_path):
    # 检查文件和目录
    if not os.path.exists(image_dir):
        raise FileNotFoundError(f"图片目录不存在: {image_dir}")
    if not os.path.exists(audio_path):
        raise FileNotFoundError(f"音频文件不存在: {audio_path}")
    
    # 获取所有图片并排序
    image_files = sorted(glob.glob(os.path.join(image_dir, "*.[jp][pn][g]")))
    if not image_files:
        raise FileNotFoundError(f"在 {image_dir} 中没有找到图片文件")
    
    print(f"找到 {len(image_files)} 个图片文件")
    
    # 确保输出目录存在
    os.makedirs(output_path, exist_ok=True)
    
    try:
        # 读取音频文件
        print(f"正在读取音频文件: {audio_path}")
        audio = AudioFileClip(audio_path)
        
        # 按批次处理图片
        for i in range(0, len(image_files), 10):
            batch_files = image_files[i:i+10]
            batch_number = i//10 + 1
            
            try:
                process_batch(batch_files, audio, batch_number, output_path)
            except Exception as e:
                print(f"处理第 {batch_number} 批时出错: {str(e)}")
                continue
        
        # 清理音频资源
        audio.close()
        print("\n所有批次处理完成！")
        
    except Exception as e:
        print(f"发生错误: {str(e)}")
        raise

if __name__ == "__main__":
    # 设置路径
    base_dir = "/Users/ocean./Downloads/24.11航海"
    image_dir = os.path.join(base_dir, "演示图")
    audio_path = os.path.join(base_dir, "biubiubiu.m4a")
    output_path = os.path.join(base_dir, "output")
    
    # 创建视频
    create_videos_from_images(image_dir, audio_path, output_path) 