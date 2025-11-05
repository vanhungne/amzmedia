'use client';

import { useEffect, useRef, useState } from 'react';

export default function SpaceBackground() {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const [isLoaded, setIsLoaded] = useState(false);

  useEffect(() => {
    // Delay loading to allow page to render first
    const loadTimeout = setTimeout(() => {
      setIsLoaded(true);
    }, 100);

    return () => clearTimeout(loadTimeout);
  }, []);

  useEffect(() => {
    if (!isLoaded) return;
    
    const canvas = canvasRef.current;
    if (!canvas) return;

    const ctx = canvas.getContext('2d');
    if (!ctx) return;
    
    let isActive = true;
    
    // Pause animation when tab is not visible
    const handleVisibilityChange = () => {
      isActive = !document.hidden;
    };
    document.addEventListener('visibilitychange', handleVisibilityChange);

    // Set canvas size
    const resizeCanvas = () => {
      canvas.width = window.innerWidth;
      canvas.height = window.innerHeight;
    };
    resizeCanvas();
    window.addEventListener('resize', resizeCanvas);

    // Star properties
    interface Star {
      x: number;
      y: number;
      size: number;
      speed: number;
      opacity: number;
      twinkleSpeed: number;
      twinklePhase: number;
    }

    const stars: Star[] = [];
    const numStars = 80; // Giảm từ 150 xuống 80 để tối ưu performance

    // Create stars
    for (let i = 0; i < numStars; i++) {
      stars.push({
        x: Math.random() * canvas.width,
        y: Math.random() * canvas.height,
        size: Math.random() * 2 + 0.5,
        speed: Math.random() * 0.5 + 0.1,
        opacity: Math.random(),
        twinkleSpeed: Math.random() * 0.02 + 0.01,
        twinklePhase: Math.random() * Math.PI * 2,
      });
    }

    // Shooting stars
    interface ShootingStar {
      x: number;
      y: number;
      length: number;
      speed: number;
      opacity: number;
      angle: number;
    }

    let shootingStars: ShootingStar[] = [];

    const createShootingStar = () => {
      shootingStars.push({
        x: Math.random() * canvas.width,
        y: Math.random() * canvas.height * 0.5,
        length: Math.random() * 80 + 40,
        speed: Math.random() * 8 + 6,
        opacity: 1,
        angle: Math.PI / 4,
      });
    };

    // Create shooting star occasionally
    const shootingStarInterval = setInterval(() => {
      if (Math.random() > 0.8) { // Giảm tần suất shooting stars
        createShootingStar();
      }
    }, 4000); // Tăng interval từ 3s lên 4s

    // Animation với throttling
    let animationFrameId: number;
    let lastFrameTime = 0;
    const targetFPS = 30; // Giới hạn ở 30 FPS thay vì 60 FPS
    const frameInterval = 1000 / targetFPS;
    
    const animate = (currentTime: number = 0) => {
      // Skip animation if tab is not active
      if (!isActive) {
        animationFrameId = requestAnimationFrame(animate);
        return;
      }
      
      const elapsed = currentTime - lastFrameTime;
      
      if (elapsed < frameInterval) {
        animationFrameId = requestAnimationFrame(animate);
        return;
      }
      
      lastFrameTime = currentTime - (elapsed % frameInterval);
      ctx.clearRect(0, 0, canvas.width, canvas.height);

      // Draw stars
      stars.forEach((star) => {
        // Twinkle effect
        star.twinklePhase += star.twinkleSpeed;
        star.opacity = 0.3 + Math.sin(star.twinklePhase) * 0.7;

        // Draw star
        ctx.beginPath();
        ctx.arc(star.x, star.y, star.size, 0, Math.PI * 2);
        ctx.fillStyle = `rgba(255, 255, 255, ${star.opacity})`;
        ctx.fill();

        // Draw glow for bigger stars
        if (star.size > 1.5) {
          const gradient = ctx.createRadialGradient(
            star.x, star.y, 0,
            star.x, star.y, star.size * 3
          );
          gradient.addColorStop(0, `rgba(147, 197, 253, ${star.opacity * 0.3})`);
          gradient.addColorStop(1, 'rgba(147, 197, 253, 0)');
          ctx.fillStyle = gradient;
          ctx.beginPath();
          ctx.arc(star.x, star.y, star.size * 3, 0, Math.PI * 2);
          ctx.fill();
        }

        // Move stars slightly
        star.y += star.speed * 0.2;
        if (star.y > canvas.height) {
          star.y = 0;
          star.x = Math.random() * canvas.width;
        }
      });

      // Draw shooting stars
      shootingStars = shootingStars.filter((shootingStar) => {
        shootingStar.opacity -= 0.01;
        
        if (shootingStar.opacity <= 0) return false;

        const endX = shootingStar.x + Math.cos(shootingStar.angle) * shootingStar.length;
        const endY = shootingStar.y + Math.sin(shootingStar.angle) * shootingStar.length;

        // Draw tail
        const gradient = ctx.createLinearGradient(
          shootingStar.x, shootingStar.y, endX, endY
        );
        gradient.addColorStop(0, `rgba(255, 255, 255, ${shootingStar.opacity})`);
        gradient.addColorStop(0.5, `rgba(147, 197, 253, ${shootingStar.opacity * 0.6})`);
        gradient.addColorStop(1, 'rgba(147, 197, 253, 0)');

        ctx.strokeStyle = gradient;
        ctx.lineWidth = 2;
        ctx.beginPath();
        ctx.moveTo(shootingStar.x, shootingStar.y);
        ctx.lineTo(endX, endY);
        ctx.stroke();

        // Move shooting star
        shootingStar.x += Math.cos(shootingStar.angle) * shootingStar.speed;
        shootingStar.y += Math.sin(shootingStar.angle) * shootingStar.speed;

        return shootingStar.x < canvas.width && shootingStar.y < canvas.height;
      });

      animationFrameId = requestAnimationFrame(animate);
    };

    animate();

    return () => {
      isActive = false;
      document.removeEventListener('visibilitychange', handleVisibilityChange);
      window.removeEventListener('resize', resizeCanvas);
      cancelAnimationFrame(animationFrameId);
      clearInterval(shootingStarInterval);
    };
  }, [isLoaded]);

  return (
    <canvas
      ref={canvasRef}
      className="fixed inset-0 pointer-events-none"
      style={{ 
        zIndex: 1,
        opacity: isLoaded ? 1 : 0,
        transition: 'opacity 0.5s ease-in-out'
      }}
    />
  );
}

