import axios from "axios";

// Cliente axios apontando para o backend FastAPI
const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || "http://localhost:8200",
  timeout: 60000,
});

export const getStats   = ()        => api.get("/stats").then((r) => r.data);
export const search     = (body)    => api.post("/search", body).then((r) => r.data);
export const facets     = (body)    => api.post("/search/facets", body).then((r) => r.data);
export const compare    = (query)   => api.post("/compare", { query }).then((r) => r.data);
export const hybrid     = (body)    => api.post("/hybrid", body).then((r) => r.data);
export const askAgent   = (body)    => api.post("/agent", body).then((r) => r.data);
export const getAnalytics = ()      => api.get("/analytics").then((r) => r.data);
export const findSimilar  = (body)  => api.post("/similar", body).then((r) => r.data);
export const reviewsRag   = (query) => api.post("/reviews-rag", { query }).then((r) => r.data);
export const hybridNative = (query) => api.post("/hybrid-native", { query }).then((r) => r.data);

export default api;
