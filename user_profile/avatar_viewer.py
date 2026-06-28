"""
StyleSync Interactive 3D Avatar Viewer

Provides an interactive HTML5 Canvas-based viewer for the generated avatar image.
Supports zoom, pan, and multi-angle view generation.
"""
import os
import base64
import streamlit as st
from typing import Optional


def _load_image_as_base64(image_path: str) -> Optional[str]:
    """Load an image file and encode as base64 for embedding in HTML."""
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    absolute_path = os.path.join(project_root, image_path)
    
    if not os.path.exists(absolute_path):
        return None
    
    try:
        with open(absolute_path, "rb") as f:
            image_bytes = f.read()
        return base64.b64encode(image_bytes).decode("utf-8")
    except Exception:
        return None


def render_interactive_avatar_viewer(avatar_image_path: str, viewer_height: int = 500):
    """
    Render an interactive 3D avatar viewer with zoom, pan, and rotation controls.
    
    Args:
        avatar_image_path: Relative path to the avatar image (e.g., "data/avatars/user123.jpg")
        viewer_height: Height of the viewer in pixels
    """
    if not avatar_image_path:
        st.info("No avatar generated yet. Upload a full-body image and generate an avatar to view it here.")
        return
    
    image_base64 = _load_image_as_base64(avatar_image_path)
    if not image_base64:
        st.error(f"Avatar image not found at {avatar_image_path}")
        return
    
    html_viewer = f"""
    <style>
        .avatar-viewer-container {{
            width: 100%;
            max-width: 600px;
            margin: 0 auto;
            border: 2px solid #e5e7eb;
            border-radius: 12px;
            overflow: hidden;
            background: #f9fafb;
        }}
        
        .avatar-viewer-toolbar {{
            background: #ffffff;
            border-bottom: 1px solid #e5e7eb;
            padding: 12px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            gap: 8px;
            flex-wrap: wrap;
        }}
        
        .viewer-controls {{
            display: flex;
            gap: 8px;
            align-items: center;
        }}
        
        .control-button {{
            background: #f3f4f6;
            border: 1px solid #d1d5db;
            border-radius: 8px;
            padding: 8px 12px;
            cursor: pointer;
            font-size: 0.85rem;
            font-weight: 600;
            color: #374151;
            transition: all 0.2s;
        }}
        
        .control-button:hover {{
            background: #e5e7eb;
            border-color: #9ca3af;
        }}
        
        .control-button.active {{
            background: #3b82f6;
            color: #ffffff;
            border-color: #2563eb;
        }}
        
        .zoom-slider {{
            width: 120px;
            height: 6px;
            border-radius: 3px;
            background: #e5e7eb;
            outline: none;
            -webkit-appearance: none;
        }}
        
        .zoom-slider::-webkit-slider-thumb {{
            -webkit-appearance: none;
            appearance: none;
            width: 16px;
            height: 16px;
            border-radius: 50%;
            background: #3b82f6;
            cursor: pointer;
        }}
        
        .zoom-slider::-moz-range-thumb {{
            width: 16px;
            height: 16px;
            border-radius: 50%;
            background: #3b82f6;
            cursor: pointer;
            border: none;
        }}
        
        .zoom-label {{
            font-size: 0.8rem;
            color: #6b7280;
            min-width: 30px;
        }}
        
        canvas#avatarCanvas {{
            display: block;
            width: 100%;
            background: #f9fafb;
            cursor: grab;
        }}
        
        canvas#avatarCanvas:active {{
            cursor: grabbing;
        }}
        
        .viewer-info {{
            background: #eff6ff;
            border-top: 1px solid #e5e7eb;
            padding: 10px 12px;
            font-size: 0.8rem;
            color: #1e40af;
            text-align: center;
        }}
    </style>
    
    <div class="avatar-viewer-container">
        <div class="avatar-viewer-toolbar">
            <div class="viewer-controls">
                <button class="control-button" id="zoomResetBtn">Reset View</button>
                <input 
                    type="range" 
                    id="zoomSlider" 
                    class="zoom-slider" 
                    min="0.5" 
                    max="3" 
                    step="0.1" 
                    value="1"
                    title="Zoom in/out with scroll or slider"
                >
                <span class="zoom-label" id="zoomLabel">100%</span>
            </div>
            <div class="viewer-controls">
                <button class="control-button" id="rotateLeftBtn" title="Rotate counter-clockwise">↺</button>
                <span style="font-size: 0.8rem; color: #9ca3af;" id="rotationLabel">0°</span>
                <button class="control-button" id="rotateRightBtn" title="Rotate clockwise">↻</button>
            </div>
        </div>
        
        <canvas id="avatarCanvas" width="600" height="{viewer_height}"></canvas>
        
        <div class="viewer-info">
            💡 Scroll to zoom | Drag to pan | Use buttons to rotate
        </div>
    </div>
    
    <script>
        const canvas = document.getElementById('avatarCanvas');
        const ctx = canvas.getContext('2d');
        const zoomSlider = document.getElementById('zoomSlider');
        const zoomLabel = document.getElementById('zoomLabel');
        const rotateLeftBtn = document.getElementById('rotateLeftBtn');
        const rotateRightBtn = document.getElementById('rotateRightBtn');
        const zoomResetBtn = document.getElementById('zoomResetBtn');
        const rotationLabel = document.getElementById('rotationLabel');
        
        const image = new Image();
        image.src = 'data:image/jpeg;base64,{image_base64}';
        
        let zoomLevel = 1;
        let panX = 0;
        let panY = 0;
        let rotation = 0;
        let isMouseDown = false;
        let mouseDownX = 0;
        let mouseDownY = 0;
        
        const draw = () => {{
            ctx.fillStyle = '#f9fafb';
            ctx.fillRect(0, 0, canvas.width, canvas.height);
            
            ctx.save();
            
            // Move to center, rotate, then draw
            ctx.translate(canvas.width / 2 + panX, canvas.height / 2 + panY);
            ctx.rotate((rotation * Math.PI) / 180);
            
            const scaledWidth = image.width * zoomLevel;
            const scaledHeight = image.height * zoomLevel;
            ctx.drawImage(image, -scaledWidth / 2, -scaledHeight / 2, scaledWidth, scaledHeight);
            
            ctx.restore();
        }};
        
        image.onload = () => {{
            draw();
        }};
        
        zoomSlider.addEventListener('input', (e) => {{
            zoomLevel = parseFloat(e.target.value);
            zoomLabel.textContent = Math.round(zoomLevel * 100) + '%';
            draw();
        }});
        
        rotateLeftBtn.addEventListener('click', () => {{
            rotation -= 15;
            if (rotation < 0) rotation += 360;
            rotationLabel.textContent = rotation + '°';
            draw();
        }});
        
        rotateRightBtn.addEventListener('click', () => {{
            rotation += 15;
            if (rotation >= 360) rotation -= 360;
            rotationLabel.textContent = rotation + '°';
            draw();
        }});
        
        zoomResetBtn.addEventListener('click', () => {{
            zoomLevel = 1;
            panX = 0;
            panY = 0;
            rotation = 0;
            zoomSlider.value = 1;
            zoomLabel.textContent = '100%';
            rotationLabel.textContent = '0°';
            draw();
        }});
        
        // Zoom with mouse wheel
        canvas.addEventListener('wheel', (e) => {{
            e.preventDefault();
            const zoomSpeed = 0.1;
            const newZoom = zoomLevel + (e.deltaY > 0 ? -zoomSpeed : zoomSpeed);
            if (newZoom >= 0.5 && newZoom <= 3) {{
                zoomLevel = newZoom;
                zoomSlider.value = zoomLevel;
                zoomLabel.textContent = Math.round(zoomLevel * 100) + '%';
                draw();
            }}
        }});
        
        // Pan with mouse drag
        canvas.addEventListener('mousedown', (e) => {{
            isMouseDown = true;
            mouseDownX = e.clientX;
            mouseDownY = e.clientY;
        }});
        
        document.addEventListener('mousemove', (e) => {{
            if (isMouseDown) {{
                const deltaX = e.clientX - mouseDownX;
                const deltaY = e.clientY - mouseDownY;
                panX += deltaX;
                panY += deltaY;
                mouseDownX = e.clientX;
                mouseDownY = e.clientY;
                draw();
            }}
        }});
        
        document.addEventListener('mouseup', () => {{
            isMouseDown = false;
        }});
        
        // Prevent context menu on right-click
        canvas.addEventListener('contextmenu', (e) => e.preventDefault());
    </script>
    """
    
    st.components.v1.html(html_viewer, height=viewer_height + 120)


def render_avatar_angle_selector(
    user_id: str,
    current_angle: str = "front",
    on_generate_angle=None
):
    """
    Render buttons to generate avatar from different angles.
    
    Args:
        user_id: The user ID for generating angle-specific avatars
        current_angle: Current viewing angle ("front", "side", "back")
        on_generate_angle: Callback function when an angle button is clicked
    """
    st.write("#### Avatar Angles")
    
    col1, col2, col3 = st.columns(3, gap="medium")
    
    with col1:
        if st.button(
            "📸 Front View",
            use_container_width=True,
            key=f"{user_id}_front_angle",
            disabled=current_angle == "front"
        ):
            if on_generate_angle:
                on_generate_angle("front")
    
    with col2:
        if st.button(
            "👤 Side View",
            use_container_width=True,
            key=f"{user_id}_side_angle",
            disabled=current_angle == "side"
        ):
            if on_generate_angle:
                on_generate_angle("side")
    
    with col3:
        if st.button(
            "🔙 Back View",
            use_container_width=True,
            key=f"{user_id}_back_angle",
            disabled=current_angle == "back"
        ):
            if on_generate_angle:
                on_generate_angle("back")
