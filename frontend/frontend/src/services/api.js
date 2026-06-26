import axios from "axios";

const API_URL = import.meta.env.VITE_API_URL;

export function classifyImage(file) {
  const formData = new FormData();
  formData.append("image", file);

  return axios.post(`${API_URL}/classify/`, formData);
}