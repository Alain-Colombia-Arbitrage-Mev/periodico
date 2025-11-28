'use client';

import { useState, useRef, useEffect } from 'react';
import { Play, Pause, Volume2, VolumeX, Maximize, Minimize, SkipBack, SkipForward } from 'lucide-react';

interface MediaPlayerProps {
  src: string;
  type: 'audio' | 'video';
  poster?: string;
  title?: string;
  className?: string;
}

export default function MediaPlayer({ src, type, poster, title, className = '' }: MediaPlayerProps) {
  const mediaRef = useRef<HTMLVideoElement | HTMLAudioElement>(null);
  const progressRef = useRef<HTMLDivElement>(null);
  const [isPlaying, setIsPlaying] = useState(false);
  const [isMuted, setIsMuted] = useState(false);
  const [isFullscreen, setIsFullscreen] = useState(false);
  const [currentTime, setCurrentTime] = useState(0);
  const [duration, setDuration] = useState(0);
  const [volume, setVolume] = useState(1);
  const [showControls, setShowControls] = useState(true);
  const controlsTimeoutRef = useRef<NodeJS.Timeout | null>(null);

  useEffect(() => {
    const media = mediaRef.current;
    if (!media) return;

    const handleTimeUpdate = () => setCurrentTime(media.currentTime);
    const handleLoadedMetadata = () => setDuration(media.duration);
    const handleEnded = () => setIsPlaying(false);

    media.addEventListener('timeupdate', handleTimeUpdate);
    media.addEventListener('loadedmetadata', handleLoadedMetadata);
    media.addEventListener('ended', handleEnded);

    return () => {
      media.removeEventListener('timeupdate', handleTimeUpdate);
      media.removeEventListener('loadedmetadata', handleLoadedMetadata);
      media.removeEventListener('ended', handleEnded);
    };
  }, []);

  // Auto-hide controls for video
  useEffect(() => {
    if (type === 'video' && isPlaying) {
      controlsTimeoutRef.current = setTimeout(() => setShowControls(false), 3000);
    }
    return () => {
      if (controlsTimeoutRef.current) clearTimeout(controlsTimeoutRef.current);
    };
  }, [isPlaying, type, showControls]);

  const togglePlay = () => {
    const media = mediaRef.current;
    if (!media) return;

    if (isPlaying) {
      media.pause();
    } else {
      media.play();
    }
    setIsPlaying(!isPlaying);
  };

  const toggleMute = () => {
    const media = mediaRef.current;
    if (!media) return;

    media.muted = !isMuted;
    setIsMuted(!isMuted);
  };

  const handleVolumeChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const media = mediaRef.current;
    if (!media) return;

    const newVolume = parseFloat(e.target.value);
    media.volume = newVolume;
    setVolume(newVolume);
    setIsMuted(newVolume === 0);
  };

  const handleProgressClick = (e: React.MouseEvent<HTMLDivElement>) => {
    const media = mediaRef.current;
    const progressBar = progressRef.current;
    if (!media || !progressBar) return;

    const rect = progressBar.getBoundingClientRect();
    const percent = (e.clientX - rect.left) / rect.width;
    media.currentTime = percent * duration;
  };

  const skip = (seconds: number) => {
    const media = mediaRef.current;
    if (!media) return;

    media.currentTime = Math.max(0, Math.min(duration, media.currentTime + seconds));
  };

  const toggleFullscreen = () => {
    const container = mediaRef.current?.parentElement?.parentElement;
    if (!container) return;

    if (!isFullscreen) {
      if (container.requestFullscreen) {
        container.requestFullscreen();
      }
    } else {
      if (document.exitFullscreen) {
        document.exitFullscreen();
      }
    }
    setIsFullscreen(!isFullscreen);
  };

  const formatTime = (time: number) => {
    const minutes = Math.floor(time / 60);
    const seconds = Math.floor(time % 60);
    return `${minutes}:${seconds.toString().padStart(2, '0')}`;
  };

  const progress = duration > 0 ? (currentTime / duration) * 100 : 0;

  // Detect media type from URL if not explicitly video
  const isYouTube = src.includes('youtube.com') || src.includes('youtu.be');
  const isVimeo = src.includes('vimeo.com');

  // For YouTube/Vimeo, render iframe embed
  if (isYouTube || isVimeo) {
    let embedUrl = src;

    if (isYouTube) {
      const videoId = src.match(/(?:youtube\.com\/(?:watch\?v=|embed\/)|youtu\.be\/)([^&\s]+)/)?.[1];
      if (videoId) {
        embedUrl = `https://www.youtube.com/embed/${videoId}`;
      }
    } else if (isVimeo) {
      const videoId = src.match(/vimeo\.com\/(\d+)/)?.[1];
      if (videoId) {
        embedUrl = `https://player.vimeo.com/video/${videoId}`;
      }
    }

    return (
      <div className={`relative w-full ${className}`}>
        {title && (
          <h4 className="text-sm font-medium mb-2 text-gray-600">{title}</h4>
        )}
        <div className="relative w-full aspect-video bg-black rounded-lg overflow-hidden">
          <iframe
            src={embedUrl}
            className="absolute inset-0 w-full h-full"
            allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
            allowFullScreen
            title={title || 'Video'}
          />
        </div>
      </div>
    );
  }

  // Audio Player
  if (type === 'audio') {
    return (
      <div className={`bg-gradient-to-r from-gray-900 to-gray-800 rounded-xl p-4 ${className}`}>
        {title && (
          <h4 className="text-white text-sm font-medium mb-3 truncate">{title}</h4>
        )}

        <audio ref={mediaRef as React.RefObject<HTMLAudioElement>} src={src} preload="metadata" />

        {/* Progress Bar */}
        <div
          ref={progressRef}
          className="h-2 bg-gray-700 rounded-full cursor-pointer mb-4 group"
          onClick={handleProgressClick}
        >
          <div
            className="h-full bg-blue-500 rounded-full relative transition-all"
            style={{ width: `${progress}%` }}
          >
            <div className="absolute right-0 top-1/2 -translate-y-1/2 w-3 h-3 bg-white rounded-full shadow opacity-0 group-hover:opacity-100 transition-opacity" />
          </div>
        </div>

        <div className="flex items-center justify-between">
          {/* Time */}
          <span className="text-gray-400 text-xs font-mono">
            {formatTime(currentTime)} / {formatTime(duration)}
          </span>

          {/* Controls */}
          <div className="flex items-center gap-3">
            <button
              onClick={() => skip(-10)}
              className="text-gray-400 hover:text-white transition"
              title="Retroceder 10s"
            >
              <SkipBack className="w-5 h-5" />
            </button>

            <button
              onClick={togglePlay}
              className="w-12 h-12 bg-blue-600 hover:bg-blue-700 rounded-full flex items-center justify-center text-white transition"
            >
              {isPlaying ? <Pause className="w-6 h-6" /> : <Play className="w-6 h-6 ml-1" />}
            </button>

            <button
              onClick={() => skip(10)}
              className="text-gray-400 hover:text-white transition"
              title="Adelantar 10s"
            >
              <SkipForward className="w-5 h-5" />
            </button>
          </div>

          {/* Volume */}
          <div className="flex items-center gap-2">
            <button onClick={toggleMute} className="text-gray-400 hover:text-white transition">
              {isMuted || volume === 0 ? <VolumeX className="w-5 h-5" /> : <Volume2 className="w-5 h-5" />}
            </button>
            <input
              type="range"
              min="0"
              max="1"
              step="0.1"
              value={isMuted ? 0 : volume}
              onChange={handleVolumeChange}
              className="w-20 h-1 bg-gray-700 rounded-full appearance-none cursor-pointer [&::-webkit-slider-thumb]:appearance-none [&::-webkit-slider-thumb]:w-3 [&::-webkit-slider-thumb]:h-3 [&::-webkit-slider-thumb]:bg-white [&::-webkit-slider-thumb]:rounded-full"
            />
          </div>
        </div>
      </div>
    );
  }

  // Video Player
  return (
    <div
      className={`relative bg-black rounded-lg overflow-hidden group ${className}`}
      onMouseMove={() => {
        setShowControls(true);
        if (controlsTimeoutRef.current) clearTimeout(controlsTimeoutRef.current);
        if (isPlaying) {
          controlsTimeoutRef.current = setTimeout(() => setShowControls(false), 3000);
        }
      }}
    >
      {title && !isFullscreen && (
        <h4 className="absolute top-0 left-0 right-0 bg-gradient-to-b from-black/70 to-transparent text-white text-sm font-medium p-4 z-10">
          {title}
        </h4>
      )}

      <video
        ref={mediaRef as React.RefObject<HTMLVideoElement>}
        src={src}
        poster={poster}
        className="w-full aspect-video object-contain cursor-pointer"
        onClick={togglePlay}
        preload="metadata"
      />

      {/* Play overlay when paused */}
      {!isPlaying && (
        <div
          className="absolute inset-0 flex items-center justify-center bg-black/30 cursor-pointer"
          onClick={togglePlay}
        >
          <div className="w-20 h-20 bg-white/90 rounded-full flex items-center justify-center hover:bg-white transition">
            <Play className="w-10 h-10 text-gray-900 ml-1" />
          </div>
        </div>
      )}

      {/* Controls */}
      <div
        className={`absolute bottom-0 left-0 right-0 bg-gradient-to-t from-black/90 to-transparent p-4 transition-opacity ${
          showControls || !isPlaying ? 'opacity-100' : 'opacity-0'
        }`}
      >
        {/* Progress Bar */}
        <div
          ref={progressRef}
          className="h-1 bg-gray-600 rounded-full cursor-pointer mb-3 group/progress"
          onClick={handleProgressClick}
        >
          <div
            className="h-full bg-red-600 rounded-full relative"
            style={{ width: `${progress}%` }}
          >
            <div className="absolute right-0 top-1/2 -translate-y-1/2 w-3 h-3 bg-red-600 rounded-full opacity-0 group-hover/progress:opacity-100 transition-opacity" />
          </div>
        </div>

        <div className="flex items-center justify-between">
          {/* Left Controls */}
          <div className="flex items-center gap-3">
            <button onClick={togglePlay} className="text-white hover:text-gray-300 transition">
              {isPlaying ? <Pause className="w-6 h-6" /> : <Play className="w-6 h-6" />}
            </button>

            <button onClick={() => skip(-10)} className="text-white hover:text-gray-300 transition">
              <SkipBack className="w-5 h-5" />
            </button>

            <button onClick={() => skip(10)} className="text-white hover:text-gray-300 transition">
              <SkipForward className="w-5 h-5" />
            </button>

            <span className="text-white text-sm font-mono">
              {formatTime(currentTime)} / {formatTime(duration)}
            </span>
          </div>

          {/* Right Controls */}
          <div className="flex items-center gap-3">
            <div className="flex items-center gap-2">
              <button onClick={toggleMute} className="text-white hover:text-gray-300 transition">
                {isMuted || volume === 0 ? <VolumeX className="w-5 h-5" /> : <Volume2 className="w-5 h-5" />}
              </button>
              <input
                type="range"
                min="0"
                max="1"
                step="0.1"
                value={isMuted ? 0 : volume}
                onChange={handleVolumeChange}
                className="w-16 h-1 bg-gray-600 rounded-full appearance-none cursor-pointer [&::-webkit-slider-thumb]:appearance-none [&::-webkit-slider-thumb]:w-3 [&::-webkit-slider-thumb]:h-3 [&::-webkit-slider-thumb]:bg-white [&::-webkit-slider-thumb]:rounded-full"
              />
            </div>

            <button onClick={toggleFullscreen} className="text-white hover:text-gray-300 transition">
              {isFullscreen ? <Minimize className="w-5 h-5" /> : <Maximize className="w-5 h-5" />}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
