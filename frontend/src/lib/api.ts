import axios from 'axios';

const getApiBaseUrl = (): string => {
  if (process.env.NEXT_PUBLIC_API_URL) {
    return process.env.NEXT_PUBLIC_API_URL;
  }
  if (typeof window !== 'undefined' && window.location && window.location.hostname) {
    return `http://${window.location.hostname}:8000`;
  }
  return 'http://localhost:8000';
};

export const api = axios.create({
  baseURL: getApiBaseUrl(),
  timeout: 300000, // 5 minutes timeout for high-MB financial documents & deep AI extraction
});

api.interceptors.request.use((config) => {
  if (typeof window !== 'undefined') {
    const token = localStorage.getItem('token');
    if (token && config.headers) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    // Update baseURL dynamically per request if needed
    if (!process.env.NEXT_PUBLIC_API_URL && window.location && window.location.hostname) {
      config.baseURL = `http://${window.location.hostname}:8000`;
    }
  }
  return config;
});

api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (!error.response) {
      // Suppress unhandled network error popups during server cold-starts
    }
    return Promise.reject(error);
  }
);

export const downloadReportFile = async (url: string, filename: string) => {
  try {
    const res = await api.get(url, { responseType: 'blob' });
    const rawContentType = res.headers['content-type'];
    const contentType = typeof rawContentType === 'string' ? rawContentType : 'application/octet-stream';
    const blob = new Blob([res.data], { type: contentType });
    const blobUrl = window.URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = blobUrl;
    link.setAttribute('download', filename);
    document.body.appendChild(link);
    link.click();
    link.remove();
    window.URL.revokeObjectURL(blobUrl);
  } catch (err) {
    console.error('Report download error:', err);
    const baseUrl = (typeof window !== 'undefined' && window.location && window.location.hostname)
      ? `http://${window.location.hostname}:8000`
      : (api.defaults.baseURL || 'http://localhost:8000');
    window.open(`${baseUrl}${url}`, '_blank');
  }
};

export default api;
