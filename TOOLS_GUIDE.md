# AI Shape Generator - Extended Tools Guide

Your AI drawing tool now has **11 powerful tools** to create and manipulate canvas shapes like advanced AI agents!

## Tool Categories

### 🎨 Core Shape Tools (4 tools)

#### 1. **generate_shapes**
Generate shapes from natural language descriptions.

**Usage:**
```
"Add 3 red circles in the top-left corner"
"Create a blue rectangle in the center"
"Make 5 green triangles scattered around"
```

**Parameters:**
- `request` (string, required): Natural language description
- `canvas_width` (integer, optional): Canvas width (default: 1200)
- `canvas_height` (integer, optional): Canvas height (default: 600)

---

#### 2. **list_shapes**
Get information about all shapes currently on the canvas.

**Usage:**
```
Lists all shapes with:
- Type (circle, rect, triangle, etc.)
- Position (x, y coordinates)
- Size (radius, width, height)
- Color
- Total shape count
```

**Parameters:**
- `shapes` (array, required): Current shapes on canvas

---

#### 3. **modify_shape**
Change properties of a specific shape.

**Usage:**
```
Modify shape 0: {"color": "#ff0000", "x": 200, "radius": 80}
Modify shape 2: {"width": 150, "height": 100}
```

**Parameters:**
- `shapes` (array, required): Current shapes
- `shape_index` (integer, required): Which shape to modify (0-based)
- `modifications` (object, required): Properties to change

**Possible modifications:**
- `color` - Hex color (#ff0000)
- `x`, `y` - Position coordinates
- `width`, `height` - Size
- `radius` - Circle radius
- `opacity` - Transparency (0-1)

---

#### 4. **delete_shape**
Remove a shape from the canvas.

**Usage:**
```
Delete shape at index 3
Remove the second shape (index 1)
```

**Parameters:**
- `shapes` (array, required): Current shapes
- `shape_index` (integer, required): Index of shape to delete

---

### 📐 Layout & Arrangement Tools (1 tool)

#### 5. **arrange_shapes**
Organize shapes in predefined layouts.

**Usage:**
```
Arrange in grid pattern
Arrange horizontally with 30px spacing
Arrange in circular pattern
```

**Parameters:**
- `shapes` (array, required): Current shapes
- `arrangement_type` (string, required): 
  - `grid` - 3x3 grid layout
  - `horizontal` - Line them up horizontally
  - `vertical` - Stack them vertically
  - `circle` - Arrange in circle pattern
- `spacing` (integer, optional): Space between shapes (default: 20px)

---

### 🎨 Color & Style Tools (2 tools)

#### 6. **generate_palette**
Create color palettes based on themes.

**Usage:**
```
Generate vibrant colors for bright designs
Generate pastel colors for soft designs
Generate ocean colors for water themes
```

**Parameters:**
- `color_scheme` (string, required):
  - `vibrant` - Bold, bright colors
  - `pastel` - Soft, light colors
  - `dark` - Deep, dark colors
  - `earth` - Natural, earthy tones
  - `ocean` - Blue, cyan, water colors
  - `sunset` - Orange, red, warm colors

**Returns:** Array of 6 hex colors you can use with shapes

---

#### 7. **apply_style_to_shapes**
Add visual effects to all shapes at once.

**Usage:**
```
Apply shadow effect to all shapes
Add outlines to all shapes
Make shapes glow with neon effect
```

**Parameters:**
- `shapes` (array, required): Current shapes
- `style` (string, required):
  - `shadow` - Drop shadow effect
  - `outline` - Black borders around shapes
  - `neon` - Glowing neon effect
  - `glass` - Transparent glass effect
  - `gradient` - Gradient fill effect

---

### ⚡ Batch Operations (1 tool)

#### 8. **batch_modify_shapes**
Change multiple shapes at once using filters.

**Usage:**
```
Change all circles to red
Make all blue shapes larger
Modify all shapes with color:#0000ff
```

**Parameters:**
- `shapes` (array, required): Current shapes
- `filter_type` (string, required):
  - `all` - Modify every shape
  - `type:circle` - Only circles
  - `type:rect` - Only rectangles
  - `type:triangle` - Only triangles
  - `color:#ff0000` - Only red shapes
- `modifications` (object, required): Properties to change

---

### 🎭 Pattern Generation (1 tool)

#### 9. **generate_pattern**
Create decorative patterns automatically.

**Usage:**
```
Create a checkerboard pattern
Generate dots in circular arrangement
Make a wave pattern
```

**Parameters:**
- `pattern_type` (string, required):
  - `checkerboard` - Black/white grid
  - `dots` - Circular dot pattern
  - `wave` - Wavy line of shapes
  - `diagonal` - Diagonal arrangement
  - `lines` - Straight lines
- `count` (integer, optional): Number of elements (default: 10)
- `canvas_width` (integer, optional): Canvas width (default: 1200)
- `canvas_height` (integer, optional): Canvas height (default: 600)

---

### 📊 Analysis Tools (1 tool)

#### 10. **analyze_canvas**
Get detailed information about canvas contents.

**Usage:**
```
Analyze canvas to see:
- Total number of shapes
- Types of shapes used
- Colors in use
- Boundaries of all shapes
```

**Parameters:**
- `shapes` (array, required): Current shapes

**Returns:**
```
{
  "total_shapes": 5,
  "shape_types": {
    "circle": 3,
    "rect": 2
  },
  "colors_used": ["#ff0000", "#0000ff"],
  "bounds": {
    "min_x": 50,
    "max_x": 1000,
    "min_y": 50,
    "max_y": 500
  }
}
```

---

### 🎯 Icon Generation (1 tool)

#### 11. **generate_icon**
Create simple vector icons.

**Usage:**
```
Generate a red heart icon
Create a blue star
Make a yellow arrow pointing right
```

**Parameters:**
- `icon_name` (string, required):
  - `heart` - Heart shape
  - `star` - Star shape
  - `arrow` - Arrow shape
  - `circle` - Circle shape
- `size` (integer, optional): Icon size in pixels (default: 100)
- `color` (string, optional): Hex color (default: #2563eb)

---

## Example Workflows

### Create a Dashboard
```
1. generate_shapes("Create 4 cards in a 2x2 grid")
2. arrange_shapes(result, "grid", 30)
3. apply_style_to_shapes(result, "shadow")
4. generate_palette("vibrant")
5. batch_modify_shapes(result, "all", {color: "#2563eb"})
```

### Design a Colorful Background
```
1. generate_pattern("dots", 12)
2. generate_palette("sunset")
3. batch_modify_shapes(result, "all", {color: "#ff6b35"})
4. apply_style_to_shapes(result, "shadow")
```

### Create Icons
```
1. generate_icon("star", 100, "#ffff00")
2. generate_icon("heart", 80, "#ff0000")
3. generate_icon("arrow", 90, "#0000ff")
4. arrange_shapes(result, "horizontal", 20)
```

### Analyze and Optimize
```
1. analyze_canvas(current_shapes)
2. batch_modify_shapes(shapes, "type:circle", {color: "#ff0000"})
3. arrange_shapes(result, "circle")
4. apply_style_to_shapes(result, "neon")
```

---

## Tips for Best Results

### Using Colors
- Use **vibrant** palette for bold designs
- Use **pastel** palette for soft, friendly designs
- Use **ocean** palette for water/nature themes
- Use **sunset** palette for warm, energetic designs

### Layout Strategies
- **Grid** - Best for dashboards, galleries
- **Circular** - Best for focus/emphasis
- **Horizontal** - Best for timelines, comparisons
- **Vertical** - Best for hierarchies, lists

### Style Combinations
- Shadow + Dark colors = Professional look
- Neon + Dark background = Modern gaming feel
- Glass + Pastel colors = Soft, modern design
- Outline + Vibrant = Comic/cartoon style

### Batch Modification Tips
- Modify all shapes with `"all"` filter
- Group by type: `"type:circle"`, `"type:rect"`
- Group by color: `"color:#ff0000"` (for red shapes)
- Combine with arrange for organized designs

---

## Tool Capability Matrix

| Task | Tools Needed | Difficulty |
|------|-------------|-----------|
| Create simple shapes | generate_shapes | ⭐ Easy |
| Organize layout | arrange_shapes | ⭐ Easy |
| Change all colors | batch_modify_shapes | ⭐⭐ Medium |
| Add visual effects | apply_style_to_shapes | ⭐⭐ Medium |
| Create patterns | generate_pattern | ⭐⭐ Medium |
| Fine-tune single shape | modify_shape | ⭐⭐ Medium |
| Full canvas redesign | All tools together | ⭐⭐⭐ Advanced |
| Analyze content | analyze_canvas | ⭐⭐⭐ Advanced |

---

## Advanced Techniques

### Creating Consistent Designs
```
1. analyze_canvas() - See what you have
2. generate_palette() - Get color scheme
3. batch_modify_shapes(all, palette) - Apply colors
4. arrange_shapes() - Organize layout
5. apply_style_to_shapes() - Add effects
```

### Responsive Design
```
1. generate_shapes() - Create base
2. list_shapes() - Check current state
3. Modify based on analysis
4. arrange_shapes() - Reorganize
5. apply_style_to_shapes() - Polish
```

### Icon Library
```
Use generate_icon() for:
- "heart" - Favorites, love
- "star" - Ratings, featured
- "arrow" - Navigation, direction
- "circle" - Buttons, indicators
```

---

## API Response Format

All tools return JSON responses. Successful responses include:
```json
{
  "success": true,
  "message": "Operation completed",
  "shapes": [...],
  "additional_data": {...}
}
```

Error responses:
```json
{
  "error": "Error message describing what went wrong"
}
```

---

## Next Steps

1. **Combine tools** - Use multiple tools in sequence for complex designs
2. **Experiment** - Try different combinations of styles and patterns
3. **Automate** - Build workflows that work with your designs
4. **Extend** - Add more tool functions for specific needs

Happy designing! 🎨
