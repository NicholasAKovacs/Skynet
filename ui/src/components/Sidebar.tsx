import React from 'react';
import type { Route } from '../types';

interface SidebarProps {
    selectedRoute: Route | null;
    totalRoutes: number;
}

const Sidebar: React.FC<SidebarProps> = ({ selectedRoute, totalRoutes }) => {
    return (
        <div className="sidebar">
            <h2>Route Explorer</h2>
            <div className="stats">
                <p><strong>Total Routes Displayed:</strong> {totalRoutes}</p>
            </div>

            {selectedRoute ? (
                <div className="route-details">
                    <h3>Selected Route</h3>
                    <div className="detail-card">
                        <h4>Origin</h4>
                        <p><strong>Code:</strong> {selectedRoute.origin}</p>
                        <p><strong>Airport:</strong> {selectedRoute.origin_name}</p>
                        <p><strong>City:</strong> {selectedRoute.origin_city}</p>
                    </div>
                    <div className="detail-card">
                        <h4>Destination</h4>
                        <p><strong>Code:</strong> {selectedRoute.dest}</p>
                        <p><strong>Airport:</strong> {selectedRoute.dest_name}</p>
                        <p><strong>City:</strong> {selectedRoute.dest_city}</p>
                    </div>
                    <div className="detail-card">
                        <h4>Statistics</h4>
                        <p><strong>Passengers:</strong> {selectedRoute.passengers.toLocaleString()}</p>
                    </div>
                </div>
            ) : (
                <div className="placeholder">
                    <p>Select a route on the map to view details.</p>
                </div>
            )}
        </div>
    );
};

export default Sidebar;
