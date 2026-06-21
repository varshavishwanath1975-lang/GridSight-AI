import os
from dotenv import load_dotenv
import streamlit.components.v1 as components

load_dotenv()

def show_google_traffic_map(location_data):
    api_key = os.getenv("GOOGLE_MAPS_API_KEY")

    if not api_key:
        components.html(
            "<h3 style='color:red;'>Google Maps API key not found. Check .env file.</h3>",
            height=100
        )
        return

    markers_js = ""

    for item in location_data:
        markers_js += f"""
        const marker_{item['id']} = new google.maps.Marker({{
            position: {{ lat: {item['lat']}, lng: {item['lng']} }},
            map: map,
            title: "{item['location']}",
            label: "{item['risk_label'][0]}"
        }});

        const info_{item['id']} = new google.maps.InfoWindow({{
            content: `
                <div style="font-family:Arial; min-width:220px;">
                    <h3>{item['location']}</h3>
                    <p><b>Status:</b> {item['risk_label']}</p>
                    <p><b>Risk:</b> {item['risk']}%</p>
                    <p><b>15 Min Forecast:</b> {item['forecast_15']}</p>
                    <p><b>30 Min Forecast:</b> {item['forecast_30']}</p>
                    <p><b>60 Min Forecast:</b> {item['forecast_60']}</p>
                    <p><b>Cases:</b> {item['cases']}</p>
                </div>
            `
        }});

        marker_{item['id']}.addListener("click", () => {{
            info_{item['id']}.open(map, marker_{item['id']});
        }});

        new google.maps.Circle({{
            strokeColor: "{item['color']}",
            strokeOpacity: 0.9,
            strokeWeight: 2,
            fillColor: "{item['color']}",
            fillOpacity: 0.30,
            map,
            center: {{ lat: {item['lat']}, lng: {item['lng']} }},
            radius: {item['radius']}
        }});

        bounds.extend(marker_{item['id']}.getPosition());
        """

    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <script src="https://maps.googleapis.com/maps/api/js?key={api_key}&libraries=visualization"></script>
    </head>

    <body style="margin:0;padding:0;">
        <div id="map" style="height:680px;width:100%;border-radius:18px;"></div>

        <script>
            const map = new google.maps.Map(document.getElementById("map"), {{
                zoom: 11,
                center: {{ lat: 12.9716, lng: 77.5946 }},
                mapTypeId: "roadmap",
                styles: [
                    {{ elementType: "geometry", stylers: [{{ color: "#1f2937" }}] }},
                    {{ elementType: "labels.text.stroke", stylers: [{{ color: "#111827" }}] }},
                    {{ elementType: "labels.text.fill", stylers: [{{ color: "#e5e7eb" }}] }},
                    {{
                        featureType: "road",
                        elementType: "geometry",
                        stylers: [{{ color: "#374151" }}]
                    }},
                    {{
                        featureType: "water",
                        elementType: "geometry",
                        stylers: [{{ color: "#0f172a" }}]
                    }}
                ]
            }});

            const bounds = new google.maps.LatLngBounds();

            const trafficLayer = new google.maps.TrafficLayer();
            trafficLayer.setMap(map);

            {markers_js}

            if (!bounds.isEmpty()) {{
                map.fitBounds(bounds);
            }}
        </script>
    </body>
    </html>
    """

    components.html(html, height=710)