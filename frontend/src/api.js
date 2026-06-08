import axios from "axios";

// Cliente axios apontando para o backend FastAPI
const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || "http://localhost:8100",
  timeout: 60000,
});

export const getStats   = ()        => api.get("/stats").then((r) => r.data);
export const search     = (body)    => api.post("/search", body).then((r) => r.data);
export const facets     = (body)    => api.post("/search/facets", body).then((r) => r.data);
export const compare    = (query)   => api.post("/compare", { query }).then((r) => r.data);
export const hybrid     = (body)    => api.post("/hybrid", body).then((r) => r.data);
export const askAgent   = (body)    => api.post("/agent", body).then((r) => r.data);

export default api;
