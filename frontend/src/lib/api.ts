import axios from 'axios';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export const api = axios.create({
  baseURL: API_BASE_URL,
});

api.interceptors.request.use((config) => {
  if (typeof window !== 'undefined') {
    const token = localStorage.getItem('token');
    if (token && config.headers) {
      config.headers.Authorization = `Bearer ${token}`;
    }
  }
  return config;
});

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
    const baseUrl = api.defaults.baseURL || 'http://localhost:8000';
    window.open(`${baseUrl}${url}`, '_blank');
  }
};

export default api;
