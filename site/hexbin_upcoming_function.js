// Hexbin Heatmap Rendering Function for Upcoming DCs
async function renderUpcomingHexbinHeatmap(containerId) {
    try {
        // Load geocoded upcoming DC data
        const response = await fetch('upcoming_dcs_geocoded.json');
        const upcomingData = await response.json();

        console.log(`Loaded ${upcomingData.length} upcoming DCs with coordinates`);

        // Clear existing content
        const container = document.getElementById(containerId);
        container.innerHTML = `
            <h3 style="text-align: center; margin-bottom: 15px;">Upcoming Data Center Projects (Hexbin Heatmap)</h3>
            <div id="upcomingHexmapContainer"></div>
            <div class="hexmap-legend">
                <h4>Project Density Legend</h4>
                <div class="legend-item"><span class="legend-color" style="background: #c7e9c0"></span> 1-2 Projects</div>
                <div class="legend-item"><span class="legend-color" style="background: #74c476"></span> 3-5 Projects</div>
                <div class="legend-item"><span class="legend-color" style="background: #31a354"></span> 6-10 Projects</div>
                <div class="legend-item"><span class="legend-color" style="background: #006d2c"></span> 11+ Projects</div>
                <p style="margin-top: 10px; font-size: 12px;">Hover over hexagons to see details. Showing ${upcomingData.length} upcoming projects.</p>
            </div>
            <div class="hexmap-tooltip"></div>
        `;

        // Set up dimensions - FORCE WIDE LANDSCAPE (2:1 ratio)
        const width = 960;
        const height = 500;
        const margin = {top: 10, right: 10, bottom: 10, left: 10};

        // Create SVG - lock into wide aspect ratio
        const svg = d3.select('#upcomingHexmapContainer')
            .append('svg')
            .attr('viewBox', `0 0 ${width} ${height}`)
            .attr('preserveAspectRatio', 'xMidYMid meet')
            .style('width', '100%')
            .style('height', 'auto');

        // Load US GeoJSON for fitSize (creates a dummy feature covering US bounds)
        const usBounds = {
            type: "FeatureCollection",
            features: [{
                type: "Feature",
                geometry: {
                    type: "Polygon",
                    coordinates: [[
                        [-125, 49], [-125, 24], [-66, 24], [-66, 49], [-125, 49]
                    ]]
                }
            }]
        };

        // Create projection - FORCE FIT TO WIDE CANVAS
        const projection = d3.geoAlbersUsa()
            .fitSize([width - margin.left - margin.right, height - margin.top - margin.bottom], usBounds);

        // Project upcoming DC coordinates
        const projectedData = upcomingData
            .map(d => {
                const projected = projection([d.longitude, d.latitude]);
                if (projected) {
                    return {
                        ...d,
                        x: projected[0],
                        y: projected[1]
                    };
                }
                return null;
            })
            .filter(d => d !== null);

        console.log(`Projected ${projectedData.length} upcoming DCs onto map`);

        // Create hexbin generator - larger radius for prominent cells
        const hexbin = d3.hexbin()
            .radius(20)
            .extent([[margin.left, margin.top], [width - margin.right, height - margin.bottom]]);

        // Generate hexbins
        const bins = hexbin(projectedData.map(d => [d.x, d.y]));

        // Color scale (green theme for upcoming projects)
        const colorScale = d3.scaleThreshold()
            .domain([1, 3, 6, 11])
            .range(['#c7e9c0', '#74c476', '#31a354', '#006d2c']);

        // Tooltip
        const tooltip = d3.select('.hexmap-tooltip');

        // Draw hexagons - prominent honeycomb cells
        svg.append('g')
            .selectAll('path')
            .data(bins)
            .join('path')
            .attr('class', 'hexagon')
            .attr('d', hexbin.hexagon())
            .attr('transform', d => `translate(${d.x},${d.y})`)
            .attr('fill', d => colorScale(d.length))
            .attr('fill-opacity', 0.9)
            .attr('stroke', '#333')
            .attr('stroke-width', 1.5)
            .on('mouseover', function(event, d) {
                // Get project details for this hexbin
                const projects = d.map(point => {
                    const project = projectedData.find(p => p.x === point[0] && p.y === point[1]);
                    return project;
                }).filter(p => p);

                const cities = [...new Set(projects.map(p => p.city))].slice(0, 5);
                const states = [...new Set(projects.map(p => p.state))].slice(0, 3);
                const totalMW = projects.reduce((sum, p) => sum + (parseFloat(p.capacity_mw) || 0), 0);
                const statuses = [...new Set(projects.map(p => p.status))].filter(s => s && s !== 'unknown');

                tooltip.style('opacity', 1)
                    .html(`
                        <strong>${d.length} Upcoming Project${d.length > 1 ? 's' : ''}</strong><br/>
                        ${totalMW > 0 ? `<strong>Total Capacity:</strong> ${totalMW.toFixed(0)} MW<br/>` : ''}
                        <strong>Status:</strong> ${statuses.length > 0 ? statuses.join(', ') : 'TBD'}<br/>
                        <strong>Locations:</strong> ${cities.join(', ')}${cities.length >= 5 ? '...' : ''}, ${states.join(', ')}
                    `)
                    .style('left', (event.pageX + 10) + 'px')
                    .style('top', (event.pageY - 10) + 'px');
            })
            .on('mouseout', function() {
                tooltip.style('opacity', 0);
            });

        console.log(`Rendered ${bins.length} hexagons for upcoming projects`);

    } catch (error) {
        console.error('Error rendering upcoming hexbin heatmap:', error);
        document.getElementById(containerId).innerHTML = `
            <p style="text-align: center; padding: 40px;">
                Unable to load upcoming projects hexbin heatmap. Please ensure geocoded data is available.
            </p>
        `;
    }
}
