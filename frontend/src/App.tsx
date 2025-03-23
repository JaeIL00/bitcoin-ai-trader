import { useEffect, useRef, useState } from 'react';
import useWebSocket from './hook/useWebsocket'

function App() {
  const logContainerRef = useRef<HTMLDivElement>(null);
  const [autoScroll, setAutoScroll] = useState<boolean>(true);
  const { isConnected, messages, error} = useWebSocket('ws://localhost:5002/ws/logs');

  // 자동 스크롤 
  useEffect(() => {
    if (logContainerRef.current && autoScroll) {
      logContainerRef.current.scrollTop = logContainerRef.current.scrollHeight;
    }
  }, [messages, autoScroll]);

  // 자동 스크롤 토글
  const toggleAutoScroll = () => {
    setAutoScroll(!autoScroll);
  };


  return (
    <div className="grid grid-rows-[auto_1fr] h-screen bg-white dark:bg-gray-900 p-4">
      {/* 헤더 */}
      <div className="flex justify-between items-center p-4 border-b border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800 shadow-md">
        <div className="flex items-center">
          <h2 className="text-xl font-semibold text-gray-800 dark:text-gray-200">로그 모니터링</h2>
          <div className={`ml-3 px-3 py-1 rounded-full text-sm font-medium flex items-center`}>
            {isConnected ? '✅' : '❌'}
          </div>
        </div>
        
        <div className="flex items-center space-x-2">
          <button 
            onClick={toggleAutoScroll}
            className={`lg:block hidden px-3 py-1 rounded-md text-sm transition-colors ${
              autoScroll 
                ? 'bg-blue-100 text-blue-800 dark:bg-blue-800 dark:text-blue-100' 
                : 'bg-gray-100 text-gray-800 dark:bg-gray-700 dark:text-gray-200'
            }`}
          >
            {autoScroll ? '자동 스크롤 ON' : '자동 스크롤 OFF'}
          </button>
        </div>
      </div>
      
      {/* 에러 알림 */}
      {error && (
        <div className="mx-4 mt-2 p-3 bg-red-100 dark:bg-red-900 text-red-800 dark:text-red-100 rounded-md">
          <p>연결 오류: {error.message || "웹소켓 연결에 문제가 발생했습니다."}</p>
        </div>
      )}

      {/* 로그 컨테이너 */}
      <div 
        ref={logContainerRef}
        className="flex-1 overflow-y-auto p-4 bg-gray-50 dark:bg-gray-900"
      >
        {messages.length === 0 && (
          <div className="flex items-center justify-center h-full text-gray-400 dark:text-gray-500">
            <p>로그 메시지가 없습니다</p>
          </div>
        )}
        
        {messages.map((log, index) => (
          <div 
            key={index} 
            className="p-3 bg-white dark:bg-gray-800 rounded-lg shadow-sm border-l-4 border-blue-500 animate-fadeIn transition-all hover:shadow-md mb-4"
          >
            <div className="flex flex-col sm:flex-row sm:items-center mb-1">
              <span className="font-mono text-sm text-gray-500 dark:text-gray-400 mr-2">
                {new Date(log.timestamp).toLocaleString()}
              </span>
              <span className="text-xs font-semibold px-2 py-0.5 rounded-full bg-blue-100 text-blue-800 dark:bg-blue-800 dark:text-blue-100 w-fit">
                {log.module.toUpperCase()}
              </span>
            </div>
            <p className="text-gray-800 dark:text-gray-200 break-words whitespace-pre-wrap font-mono text-sm text-left">
              {log.message}
            </p>
          </div>
        ))}
      </div>

      {/* 자동 스크롤 표시기 (모바일에서 좀 더 접근하기 쉽게) */}
      <div className="sm:hidden fixed bottom-4 right-4">
        <button
          onClick={toggleAutoScroll}
          className={`p-3 rounded-full shadow-lg ${
            autoScroll 
              ? 'bg-blue-500 text-white' 
              : 'bg-gray-200 text-gray-800 dark:bg-gray-700 dark:text-gray-200'
          }`}
        >
          <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
            <polyline points="7 13 12 18 17 13"></polyline>
          </svg>
        </button>
      </div>
    </div>
  );
}

export default App
