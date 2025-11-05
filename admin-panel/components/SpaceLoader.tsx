'use client';

export default function SpaceLoader({ message = 'Đang tải...' }: { message?: string }) {
  return (
    <div className="card text-center py-16 relative overflow-hidden">
      {/* Animated background glow */}
      <div className="absolute inset-0 opacity-30">
        <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-64 h-64 bg-purple-400 rounded-full blur-3xl animate-pulse"></div>
        <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-48 h-48 bg-blue-400 rounded-full blur-2xl animate-pulse" style={{ animationDelay: '0.5s' }}></div>
      </div>

      {/* Orbital loader */}
      <div className="relative w-24 h-24 mx-auto mb-6">
        {/* Center star */}
        <div className="absolute inset-0 flex items-center justify-center">
          <div className="w-8 h-8 rounded-full bg-gradient-to-br from-purple-500 to-pink-500 animate-pulse" style={{ boxShadow: '0 0 30px rgba(147, 51, 234, 0.6)' }}></div>
        </div>

        {/* Orbiting planets */}
        <div className="absolute inset-0" style={{ animation: 'orbit 3s linear infinite' }}>
          <div className="w-4 h-4 rounded-full bg-gradient-to-br from-blue-400 to-cyan-400" style={{ boxShadow: '0 0 20px rgba(59, 130, 246, 0.6)' }}></div>
        </div>
        
        <div className="absolute inset-0" style={{ animation: 'orbit 2s linear infinite', animationDirection: 'reverse' }}>
          <div className="w-3 h-3 rounded-full bg-gradient-to-br from-pink-400 to-purple-400" style={{ boxShadow: '0 0 15px rgba(236, 72, 153, 0.6)' }}></div>
        </div>

        <div className="absolute inset-0" style={{ animation: 'orbit 4s linear infinite' }}>
          <div className="w-2.5 h-2.5 rounded-full bg-gradient-to-br from-yellow-400 to-orange-400" style={{ boxShadow: '0 0 15px rgba(251, 191, 36, 0.6)' }}></div>
        </div>

        {/* Rotating ring */}
        <div className="absolute inset-0 border-2 border-dashed rounded-full animate-spin" style={{ borderColor: 'rgba(147, 51, 234, 0.3)', animationDuration: '8s' }}></div>
        <div className="absolute inset-2 border-2 border-dashed rounded-full animate-spin" style={{ borderColor: 'rgba(59, 130, 246, 0.3)', animationDuration: '6s', animationDirection: 'reverse' }}></div>
      </div>

      {/* Message */}
      <p className="text-gray-700 font-bold text-lg relative z-10 bg-gradient-to-r from-purple-600 via-blue-600 to-pink-600 bg-clip-text text-transparent animate-pulse">
        {message}
      </p>

      {/* Loading dots */}
      <div className="flex justify-center gap-2 mt-4 relative z-10">
        <div className="w-2 h-2 rounded-full bg-purple-500 animate-bounce" style={{ animationDelay: '0s' }}></div>
        <div className="w-2 h-2 rounded-full bg-blue-500 animate-bounce" style={{ animationDelay: '0.2s' }}></div>
        <div className="w-2 h-2 rounded-full bg-pink-500 animate-bounce" style={{ animationDelay: '0.4s' }}></div>
      </div>
    </div>
  );
}

