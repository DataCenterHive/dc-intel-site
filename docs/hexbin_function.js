// Hexbin Heatmap Rendering Function
async function renderHexbinHeatmap(containerId) {
    try {
        // Load geocoded data
        const response = await fetch('datacenters_geocoded.json');
        const dcData = await response.json();

        console.log(`Loaded ${dcData.length} DCs with coordinates`);

        // Clear existing content
        const container = document.getElementById(containerId);
        container.innerHTML = `
            <h3 style="text-align: center; margin-bottom: 15px;">Data Center Geographic Distribution (Hexbin Heatmap)</h3>
            <div id="hexmapContainer"></div>
            <div class="hexmap-legend">
                <h4>Density Legend</h4>
                <div class="legend-item"><span class="legend-color" style="background: #fee5d9"></span> 1-2 DCs</div>
                <div class="legend-item"><span class="legend-color" style="background: #fcae91"></span> 3-5 DCs</div>
                <div class="legend-item"><span class="legend-color" style="background: #fb6a4a"></span> 6-10 DCs</div>
                <div class="legend-item"><span class="legend-color" style="background: #de2d26"></span> 11-20 DCs</div>
                <div class="legend-item"><span class="legend-color" style="background: #a50f15"></span> 20+ DCs</div>
                <p style="margin-top: 10px; font-size: 12px;">Hover over hexagons to see details. Showing ${dcData.length} geocoded data centers.</p>
            </div>
            <div class="hexmap-tooltip"></div>
        `;

        // Set up dimensions - FORCE WIDE LANDSCAPE (2:1 ratio)
        const width = 960;
        const height = 500;
        const margin = {top: 10, right: 10, bottom: 10, left: 10};

        // Create SVG - lock into wide aspect ratio
        const svg = d3.select('#hexmapContainer')
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

        // Project DC coordinates
        const projectedData = dcData
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

        console.log(`Projected ${projectedData.length} DCs onto map`);

        // Create hexbin generator - larger radius for prominent cells
        const hexbin = d3.hexbin()
            .radius(20)
            .extent([[margin.left, margin.top], [width - margin.right, height - margin.bottom]]);

        // Generate hexbins
        const bins = hexbin(projectedData.map(d => [d.x, d.y]));

        // Color scale
        const colorScale = d3.scaleThreshold()
            .domain([1, 3, 6, 11, 20])
            .range(['#fee5d9', '#fcae91', '#fb6a4a', '#de2d26', '#a50f15']);

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
                // Get DC details for this hexbin
                const dcs = d.map(point => {
                    const dc = projectedData.find(dc => dc.x === point[0] && dc.y === point[1]);
                    return dc;
                }).filter(dc => dc);

                const providers = [...new Set(dcs.map(dc => dc.provider))].slice(0, 5);
                const cities = [...new Set(dcs.map(dc => dc.city))].slice(0, 5);

                tooltip.style('opacity', 1)
                    .html(`
                        <strong>${d.length} Data Center${d.length > 1 ? 's' : ''}</strong><br/>
                        <strong>Providers:</strong> ${providers.join(', ')}${providers.length < dcs.length ? '...' : ''}<br/>
                        <strong>Cities:</strong> ${cities.join(', ')}${cities.length < [...new Set(dcs.map(dc => dc.city))].length ? '...' : ''}
                    `)
                    .style('left', (event.pageX + 10) + 'px')
                    .style('top', (event.pageY - 10) + 'px');
            })
            .on('mouseout', function() {
                tooltip.style('opacity', 0);
            });

        console.log(`Rendered ${bins.length} hexagons`);

    } catch (error) {
        console.error('Error rendering hexbin heatmap:', error);
        document.getElementById(containerId).innerHTML = `
            <p style="text-align: center; padding: 40px;">
                Unable to load hexbin heatmap. Please ensure geocoded data is available.
            </p>
        `;
    }
}
