import axios from "axios";

const API = axios.create({
  baseURL: "http://127.0.0.1:8000",
  timeout: 30000,
});

export default API;

export const getPortfolio = () => API.get("/portfolio");
export const getBacktestResults = () => API.get("/backtest/results");
export const getRegime = () => API.get("/regime");
export const getRisk = () => API.get("/risk");
export const getState = () => API.get("/state");
export const getEngineLog = (limit = 100) => API.get("/engine/log", { params: { limit } });
export const runBacktest = (data) => API.post("/run_backtest", data);
export const runStressTest = (data) => API.post("/stress_test", data || {});
export const startEngine = () => API.post("/start");
export const stopEngine = () => API.post("/stop");
export const addFunds = (data) => API.post("/add-funds", data);
export const withdraw = (data) => API.post("/withdraw", data);
export const setRiskLevel = (level) => API.post("/risk-level", { level });
export const rebalance = () => API.post("/rebalance");
