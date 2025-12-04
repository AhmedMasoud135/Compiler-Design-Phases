import tkinter as tk
from typing import List, Dict, Tuple, Set, Optional
import math

def draw_dfa_sequential(canvas, states, goto_table, reduction_states, theme):
    """Draw DFA with enhanced sequential layout."""
    canvas.delete('all')
    
    if not states:
        canvas.create_text(
            400, 300,
            text="No DFA available - Build parser first",
            font=('Arial', 16, 'bold'),
            fill=theme['gold']
        )
        return
    
    num_states = len(states)
    
    # Compute hierarchical layout
    positions = compute_hierarchical_layout(num_states, canvas, goto_table)
    
    # Draw transitions with better routing
    draw_enhanced_transitions(canvas, goto_table, positions, theme)
    
    # Draw states on top
    draw_enhanced_states(canvas, states, positions, reduction_states, theme)

def compute_hierarchical_layout(num_states, canvas, goto_table):
    """Compute hierarchical layout for states."""
    try:
        canvas_width = int(canvas.cget('width'))
        canvas_height = int(canvas.cget('height'))
    except:
        canvas_width = 900
        canvas_height = 650
    
    # Group states by levels
    levels = assign_states_to_levels(num_states, goto_table)
    
    positions = {}
    margin_x = 100
    margin_y = 80
    available_width = canvas_width - 2 * margin_x
    available_height = canvas_height - 2 * margin_y
    
    num_levels = len(levels)
    if num_levels == 0:
        return positions
    
    level_height = available_height / max(num_levels, 1)
    
    for level_idx, states_in_level in enumerate(levels):
        y = margin_y + level_idx * level_height
        num_states_in_level = len(states_in_level)
        
        if num_states_in_level == 1:
            x = canvas_width / 2
            positions[states_in_level[0]] = (x, y)
        else:
            state_width = available_width / (num_states_in_level + 1)
            for i, state_id in enumerate(states_in_level):
                x = margin_x + (i + 1) * state_width
                positions[state_id] = (x, y)
    
    return positions

def assign_states_to_levels(num_states, goto_table):
    """Assign states to hierarchical levels using BFS."""
    if num_states == 0:
        return []
    
    adjacency = {i: [] for i in range(num_states)}
    for (from_state, symbol), to_state in goto_table.items():
        if to_state not in adjacency[from_state]:
            adjacency[from_state].append(to_state)
    
    visited = {0}
    levels = [[0]]
    current_level = [0]
    
    while current_level:
        next_level = []
        for state in current_level:
            for neighbor in adjacency.get(state, []):
                if neighbor not in visited:
                    visited.add(neighbor)
                    next_level.append(neighbor)
        
        if next_level:
            levels.append(next_level)
            current_level = next_level
        else:
            break
    
    unvisited = [i for i in range(num_states) if i not in visited]
    if unvisited:
        levels.append(unvisited)
    
    return levels

def draw_enhanced_transitions(canvas, goto_table, positions, theme):
    """Draw enhanced transitions with better routing and labels."""
    transitions = {}
    for (from_state, symbol), to_state in goto_table.items():
        if from_state not in positions or to_state not in positions:
            continue
        
        key = (from_state, to_state)
        if key not in transitions:
            transitions[key] = []
        transitions[key].append(str(symbol))
    
    for (from_state, to_state), symbols in transitions.items():
        x1, y1 = positions[from_state]
        x2, y2 = positions[to_state]
        
        if from_state == to_state:
            draw_self_loop(canvas, x1, y1, symbols, theme)
            continue
        
        dx = x2 - x1
        dy = y2 - y1
        distance = math.sqrt(dx**2 + dy**2)
        
        if distance < 1:
            continue
        
        offset = 0
        if (to_state, from_state) in transitions:
            offset = 20
        
        mid_x = (x1 + x2) / 2
        mid_y = (y1 + y2) / 2
        
        perp_x = -dy / distance * offset
        perp_y = dx / distance * offset
        
        control_x = mid_x + perp_x
        control_y = mid_y + perp_y
        
        draw_curved_arrow(canvas, x1, y1, x2, y2, control_x, control_y, theme)
        
        # Draw label with background
        label_text = ', '.join(symbols)
        label_id = canvas.create_text(control_x, control_y, text=label_text, 
                                      font=('Arial', 10, 'bold'), fill='black')
        text_bbox = canvas.bbox(label_id)
        
        if text_bbox:
            padding = 4
            canvas.create_rectangle(
                text_bbox[0] - padding, text_bbox[1] - padding,
                text_bbox[2] + padding, text_bbox[3] + padding,
                fill=theme['label_bg'],
                outline=theme['dark_gold'],
                width=1
            )
            canvas.create_text(
                control_x, control_y,
                text=label_text,
                font=('Arial', 10, 'bold'),
                fill='black'
            )

def draw_curved_arrow(canvas, x1, y1, x2, y2, cx, cy, theme):
    """Draw a curved arrow using quadratic bezier curve."""
    points = []
    steps = 20
    for i in range(steps + 1):
        t = i / steps
        x = (1-t)**2 * x1 + 2*(1-t)*t * cx + t**2 * x2
        y = (1-t)**2 * y1 + 2*(1-t)*t * cy + t**2 * y2
        points.extend([x, y])
    
    canvas.create_line(
        points,
        fill=theme['dark_gold'],
        width=2,
        smooth=True
    )
    
    t = 0.95
    x_end = (1-t)**2 * x1 + 2*(1-t)*t * cx + t**2 * x2
    y_end = (1-t)**2 * y1 + 2*(1-t)*t * cy + t**2 * y2
    angle = math.atan2(y2 - y_end, x2 - x_end)
    arrow_size = 12
    
    arrow_points = [
        x2, y2,
        x2 - arrow_size * math.cos(angle - math.pi/6),
        y2 - arrow_size * math.sin(angle - math.pi/6),
        x2 - arrow_size * math.cos(angle + math.pi/6),
        y2 - arrow_size * math.sin(angle + math.pi/6)
    ]
    
    canvas.create_polygon(
        arrow_points,
        fill=theme['dark_gold'],
        outline=theme['dark_gold']
    )

def draw_self_loop(canvas, x, y, symbols, theme):
    """Draw self-loop on a state."""
    radius = 50
    
    canvas.create_arc(
        x - radius, y - radius - 30,
        x + radius, y - radius + 30,
        start=30, extent=300,
        outline=theme['dark_gold'],
        width=2,
        style=tk.ARC
    )
    
    arrow_x = x + radius * 0.7
    arrow_y = y - radius - 10
    canvas.create_polygon(
        arrow_x, arrow_y,
        arrow_x - 8, arrow_y - 8,
        arrow_x - 5, arrow_y,
        fill=theme['dark_gold'],
        outline=theme['dark_gold']
    )
    
    label_text = ', '.join(symbols)
    label_y = y - radius - 45
    
    label_id = canvas.create_text(x, label_y, text=label_text, font=('Arial', 10, 'bold'))
    bbox = canvas.bbox(label_id)
    
    if bbox:
        canvas.create_rectangle(
            bbox[0] - 4, bbox[1] - 4,
            bbox[2] + 4, bbox[3] + 4,
            fill=theme['label_bg'],
            outline=theme['dark_gold'],
            width=1
        )
        canvas.create_text(
            x, label_y,
            text=label_text,
            font=('Arial', 10, 'bold'),
            fill='black'
        )

def draw_enhanced_states(canvas, states, positions, reduction_states, theme):
    """Draw enhanced state nodes."""
    radius = 35
    
    for i, state in enumerate(states):
        if i not in positions:
            continue
        
        x, y = positions[i]
        
        is_reduction = i in reduction_states
        is_start = i == 0
        
        if is_start:
            fill = theme['start_state']
            outline = theme['gold']
            outline_width = 4
        elif is_reduction:
            fill = theme['accept_state']
            outline = theme['gold']
            outline_width = 3
        else:
            fill = theme['normal_state']
            outline = theme['gold']
            outline_width = 2
        
        if is_start or is_reduction:
            canvas.create_oval(
                x - radius - 5, y - radius - 5,
                x + radius + 5, y + radius + 5,
                fill='',
                outline=theme['gold'],
                width=1
            )
        
        canvas.create_oval(
            x - radius, y - radius,
            x + radius, y + radius,
            fill=fill,
            outline=outline,
            width=outline_width
        )
        
        canvas.create_text(
            x, y,
            text=str(i),
            font=('Arial', 14, 'bold'),
            fill=theme['state_text']
        )
        
        if is_start:
            canvas.create_text(
                x, y + radius + 15,
                text="START",
                font=('Arial', 8, 'bold'),
                fill=theme['gold']
            )
        elif is_reduction:
            canvas.create_text(
                x, y + radius + 15,
                text="REDUCE",
                font=('Arial', 8, 'bold'),
                fill=theme['gold']
            )

def draw_parse_result_indicator(canvas, success, theme):
    """Draw accept/reject indicator."""
    canvas.delete('result_indicator')
    
    try:
        canvas_width = int(canvas.cget('width'))
    except:
        canvas_width = 380
    
    x = canvas_width / 2
    y = 40
    
    if success:
        color = theme['success']
        text = "✓ ACCEPTED"
        bg_width = 100
    else:
        color = theme['error']
        text = "✗ REJECTED"
        bg_width = 110
    
    canvas.create_rectangle(
        x - bg_width, y - 25,
        x + bg_width, y + 25,
        fill=color,
        outline=theme['gold'],
        width=3,
        tags='result_indicator'
    )
    
    canvas.create_text(
        x, y,
        text=text,
        font=('Arial', 16, 'bold'),
        fill='white',
        tags='result_indicator'
    )
