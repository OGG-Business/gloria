import { useState, useEffect } from 'react';
import { useQuery, useMutation, useQueryClient } from 'react-query';
import { toast } from 'react-hot-toast';

import apiService from '../services/api';
import { Notification } from '../types';

export const useNotifications = () => {
  const [unreadCount, setUnreadCount] = useState(0);
  const queryClient = useQueryClient();

  // Fetch notifications
  const { data: notifications = [], refetch } = useQuery<Notification[]>(
    'notifications',
    () => apiService.getNotifications(1, 50).then(res => res.items),
    {
      refetchInterval: 30000, // Refetch every 30 seconds
      onSuccess: (data) => {
        const unread = data.filter(n => !n.is_read).length;
        setUnreadCount(unread);
      }
    }
  );

  // Mark notification as read
  const markAsReadMutation = useMutation(
    (notificationId: string) => apiService.markNotificationAsRead(notificationId),
    {
      onSuccess: () => {
        queryClient.invalidateQueries('notifications');
        toast.success('Notification marked as read');
      },
      onError: () => {
        toast.error('Failed to mark notification as read');
      }
    }
  );

  // Mark all notifications as read
  const markAllAsReadMutation = useMutation(
    () => apiService.markAllNotificationsAsRead(),
    {
      onSuccess: () => {
        queryClient.invalidateQueries('notifications');
        setUnreadCount(0);
        toast.success('All notifications marked as read');
      },
      onError: () => {
        toast.error('Failed to mark notifications as read');
      }
    }
  );

  // WebSocket connection for real-time notifications
  useEffect(() => {
    const connectWebSocket = () => {
      try {
        const wsUrl = apiService.getWebSocketUrl();
        const ws = new WebSocket(wsUrl);

        ws.onopen = () => {
          console.log('WebSocket connected for notifications');
        };

        ws.onmessage = (event) => {
          try {
            const data = JSON.parse(event.data);
            if (data.type === 'notification') {
              // Add new notification to the list
              queryClient.setQueryData('notifications', (old: Notification[] = []) => {
                return [data.notification, ...old];
              });
              
              // Update unread count
              setUnreadCount(prev => prev + 1);
              
              // Show toast notification
              toast(data.notification.message, {
                duration: 5000,
                icon: getNotificationIcon(data.notification.type)
              });
            }
          } catch (error) {
            console.error('Failed to parse WebSocket message:', error);
          }
        };

        ws.onclose = () => {
          console.log('WebSocket disconnected, attempting to reconnect...');
          setTimeout(connectWebSocket, 5000);
        };

        ws.onerror = (error) => {
          console.error('WebSocket error:', error);
        };

        return ws;
      } catch (error) {
        console.error('Failed to connect WebSocket:', error);
        return null;
      }
    };

    const ws = connectWebSocket();

    return () => {
      if (ws) {
        ws.close();
      }
    };
  }, [queryClient]);

  const markAsRead = (notificationId: string) => {
    markAsReadMutation.mutate(notificationId);
  };

  const markAllAsRead = () => {
    markAllAsReadMutation.mutate();
  };

  const refreshNotifications = () => {
    refetch();
  };

  return {
    notifications,
    unreadCount,
    markAsRead,
    markAllAsRead,
    refreshNotifications,
    isLoading: false
  };
};

// Helper function to get notification icon
const getNotificationIcon = (type: string) => {
  switch (type) {
    case 'transfer_completed':
      return '✅';
    case 'transfer_failed':
      return '❌';
    case 'kyc_approved':
      return '✅';
    case 'kyc_rejected':
      return '❌';
    case 'account_suspended':
      return '⚠️';
    case 'security_alert':
      return '🚨';
    default:
      return '📢';
  }
};