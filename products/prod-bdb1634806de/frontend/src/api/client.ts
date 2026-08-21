import axios from 'axios';

const apiClient = axios.create({
  baseURL: '/',
  withCredentials: true,
});

apiClient.interceptors.response.use(
  response => response,
  error => {
    if (error.response?.status === 401 && window.location.pathname !== '/operator') {
      window.location.href='./operator';
    }
    return Promise.reject(error);
  }
);

export default apiClient;
