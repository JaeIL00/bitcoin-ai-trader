// useWebSocket.ts
import { useState, useEffect, useCallback, useRef } from 'react';

// WebSocket 옵션 인터페이스
interface WebSocketOptions {
  reconnectAttempts?: number;
  reconnectInterval?: number;
  autoReconnect?: boolean;
}

// 이벤트 리스너 타입 정의
type EventListenerMap = {
  open: ((event: Event) => void)[];
  message: ((data: any) => void)[];
  close: ((event: CloseEvent) => void)[];
  error: ((event: Event) => void)[];
  [key: string]: ((event: any) => void)[];
};

// 훅 반환 타입
interface WebSocketHookReturn {
  isConnected: boolean;
  messages: any[];
  error: Error | null;
  sendMessage: (data: any) => boolean;
  connect: () => void;
  disconnect: () => void;
  addEventListener: (event: string, callback: (event: any) => void) => () => void;
  clearMessages: () => void;
}

/**
 * WebSocket 연결을 관리하는 React 커스텀 훅
 * @param url - WebSocket 서버 URL
 * @param options - 설정 옵션
 * @returns WebSocket 상태와 관련 함수들
 */
const useWebSocket = (url: string, options: WebSocketOptions = {}): WebSocketHookReturn => {
  // 기본 옵션 설정
  const defaultOptions: Required<WebSocketOptions> = {
    reconnectAttempts: 5,
    reconnectInterval: 3000,
    autoReconnect: true,
  };
  
  const config = { ...defaultOptions, ...options };
  
  // 상태 관리
  const [isConnected, setIsConnected] = useState<boolean>(false);
  const [messages, setMessages] = useState<any[]>([]);
  const [error, setError] = useState<Error | null>(null);
  
  // refs로 관리하는 변수들
  const socketRef = useRef<WebSocket | null>(null);
  const reconnectAttemptsRef = useRef<number>(0);
  const reconnectTimerRef = useRef<number | null>(null);
  const eventListenersRef = useRef<EventListenerMap>({
    open: [],
    message: [],
    close: [],
    error: []
  });
  
  // 자원 정리 헬퍼 함수
  const cleanup = useCallback(() => {
    if (socketRef.current) {
      socketRef.current.onopen = null;
      socketRef.current.onmessage = null;
      socketRef.current.onclose = null;
      socketRef.current.onerror = null;
      
      if (socketRef.current.readyState === WebSocket.OPEN) {
        socketRef.current.close();
      }
      socketRef.current = null;
    }
    
    if (reconnectTimerRef.current !== null) {
      window.clearTimeout(reconnectTimerRef.current);
      reconnectTimerRef.current = null;
    }
  }, []);
  
  // 메시지 전송 함수
  const sendMessage = useCallback((data: any): boolean => {
    if (socketRef.current?.readyState === WebSocket.OPEN) {
      socketRef.current.send(typeof data === 'string' ? data : JSON.stringify(data));
      return true;
    }
    return false;
  }, []);
  
  // 연결 함수
  const connect = useCallback(() => {
    // 기존 연결 정리
    cleanup();
    
    try {
      // 새 WebSocket 연결 생성
      socketRef.current = new WebSocket(url);
      
      // 연결 성공 이벤트
      socketRef.current.onopen = (event: Event) => {
        console.log('WebSocket 연결 성공! 🎉');
        setIsConnected(true);
        reconnectAttemptsRef.current = 0;
        setError(null);
        
        // 등록된 이벤트 리스너 호출
        if (eventListenersRef.current.open) {
          eventListenersRef.current.open.forEach(listener => listener(event));
        }
      };
      
      // 메시지 수신 이벤트
      socketRef.current.onmessage = (event: MessageEvent) => {
        let parsedData: any;
        
        // JSON 파싱 시도
        try {
          parsedData = JSON.parse(event.data);
        } catch (e) {
          parsedData = event.data;
        }
        
        // 메시지 상태 업데이트
        setMessages(prev => {
          if(prev.length >=100) return [parsedData]
          return [...prev, parsedData]
        });
        
        // 등록된 이벤트 리스너 호출
        if (eventListenersRef.current.message) {
          eventListenersRef.current.message.forEach(listener => listener(parsedData));
        }
      };
      
      // 연결 종료 이벤트
      socketRef.current.onclose = (event: CloseEvent) => {
        console.log('WebSocket 연결 종료');
        setIsConnected(false);
        
        // 등록된 이벤트 리스너 호출
        if (eventListenersRef.current.close) {
          eventListenersRef.current.close.forEach(listener => listener(event));
        }
        
        // 자동 재연결 설정
        if (config.autoReconnect && reconnectAttemptsRef.current < config.reconnectAttempts) {
          console.log(`${config.reconnectInterval / 1000}초 후 재연결 시도...`);
          reconnectTimerRef.current = window.setTimeout(() => {
            reconnectAttemptsRef.current += 1;
            connect();
          }, config.reconnectInterval);
        } else if (reconnectAttemptsRef.current >= config.reconnectAttempts) {
          setError(new Error('최대 재연결 시도 횟수 초과'));
        }
      };
      
      // 에러 이벤트
      socketRef.current.onerror = (event: Event) => {
        console.error('WebSocket 오류:', event);
        setError(new Error('WebSocket 연결 오류'));
        
        // 등록된 이벤트 리스너 호출
        if (eventListenersRef.current.error) {
          eventListenersRef.current.error.forEach(listener => listener(event));
        }
      };
      
    } catch (error) {
      console.error('WebSocket 초기화 오류:', error);
      setError(error instanceof Error ? error : new Error('알 수 없는 오류'));
    }
  }, [url, config.autoReconnect, config.reconnectAttempts, config.reconnectInterval, cleanup]);
  
  // 연결 종료 함수
  const disconnect = useCallback(() => {
    if (socketRef.current?.readyState === WebSocket.OPEN) {
      socketRef.current.close();
    }
    cleanup();
  }, [cleanup]);
  
  // 이벤트 리스너 등록 함수
  const addEventListener = useCallback((event: string, callback: (event: any) => void) => {
    if (!eventListenersRef.current[event]) {
      eventListenersRef.current[event] = [];
    }
    eventListenersRef.current[event].push(callback);
    
    // 클린업 함수 반환
    return () => {
      if (eventListenersRef.current[event]) {
        eventListenersRef.current[event] = eventListenersRef.current[event].filter(
          cb => cb !== callback
        );
      }
    };
  }, []);
  
  // 메시지 기록 초기화
  const clearMessages = useCallback(() => {
    setMessages([]);
  }, []);
  
  // 컴포넌트 마운트 시 연결 시작, 언마운트 시 정리
  useEffect(() => {
    connect();
    
    return () => {
      cleanup();
    };
  }, [connect, cleanup]);
  
  // 반환값 - 상태와 메서드들
  return {
    isConnected,
    messages,
    error,
    sendMessage,
    connect,
    disconnect,
    addEventListener,
    clearMessages,
  };
};

export default useWebSocket;