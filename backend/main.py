from fastapi import FastAPI
from pydantic import BaseModel
from services.routing import get_optimized_route
from services.pollution import get_pollution_data
from services.emissions import predict_emissions

app = FastAPI()

class RouteRequest(BaseModel):
    start_lat: float
    start_lng: float
    end_lat: float
    end_lng: float
    vehicle_type: str  # "ev", "diesel", etc.

@app.get("/")
def root():
    return {"message": "Delivery Optimizer API is running!"}

@app.post("/optimize-route")
def optimize_route(req: RouteRequest):
    # Step 1: Get route from routing API
    route_info = get_optimized_route(req.start_lat, req.start_lng, req.end_lat, req.end_lng)

    # Step 2: Get pollution info along the route
    pollution_data = get_pollution_data(req.end_lat, req.end_lng)

    # Step 3: Estimate emissions
    co2_estimate = predict_emissions(route_info, pollution_data, req.vehicle_type)

    return {
        "optimized_route": route_info,
        "pollution_data": pollution_data,
        "estimated_co2": co2_estimate
    }