import React from 'react';
import { MapContainer, TileLayer, Polyline, CircleMarker, Popup, useMap } from 'react-leaflet';
import 'leaflet/dist/leaflet.css';
import L from 'leaflet';
import type { Route } from '../types';

interface MapProps {
    routes: Route[];
    selectedRoute: Route | null;
    onSelectRoute: (route: Route | null) => void;
}

// Component to fit bounds to routes
const FitBounds = ({ routes }: { routes: Route[] }) => {
    const map = useMap();

    React.useEffect(() => {
        if (routes.length > 0) {
            const bounds = routes.reduce((acc, route) => {
                acc.extend([route.origin_lat, route.origin_lon]);
                acc.extend([route.dest_lat, route.dest_lon]);
                return acc;
            }, new L.LatLngBounds([routes[0].origin_lat, routes[0].origin_lon], [routes[0].origin_lat, routes[0].origin_lon]));

            map.fitBounds(bounds, { padding: [50, 50] });
        }
    }, [routes, map]);

    return null;
};

const Map: React.FC<MapProps> = ({ routes, selectedRoute, onSelectRoute }) => {
    return (
        <MapContainer center={[39.8283, -98.5795]} zoom={4} style={{ height: '100%', width: '100%' }}>
            <TileLayer
                attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
                url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
            />
            <FitBounds routes={routes} />

            {routes.map((route, index) => {
                const isSelected = selectedRoute === route;
                const color = isSelected ? '#ff0000' : '#3388ff';
                const weight = isSelected ? 5 : 2;
                const opacity = isSelected ? 1 : 0.5;

                return (
                    <React.Fragment key={index}>
                        <Polyline
                            positions={[
                                [route.origin_lat, route.origin_lon],
                                [route.dest_lat, route.dest_lon]
                            ]}
                            pathOptions={{ color, weight, opacity }}
                            eventHandlers={{
                                click: () => onSelectRoute(route)
                            }}
                        />
                        <CircleMarker
                            center={[route.origin_lat, route.origin_lon]}
                            radius={3}
                            pathOptions={{ color: 'black', fillColor: 'white', fillOpacity: 1 }}
                        >
                            <Popup>{route.origin_name} ({route.origin})</Popup>
                        </CircleMarker>
                        <CircleMarker
                            center={[route.dest_lat, route.dest_lon]}
                            radius={3}
                            pathOptions={{ color: 'black', fillColor: 'white', fillOpacity: 1 }}
                        >
                            <Popup>{route.dest_name} ({route.dest})</Popup>
                        </CircleMarker>
                    </React.Fragment>
                );
            })}
        </MapContainer>
    );
};

export default Map;
