# NeuronAI Labs - IT Company Website

A modern, professional full-stack IT company website built with Next.js (frontend) and FastAPI (backend). Features a refined, elegant design with clean typography, generous whitespace, and sophisticated glassmorphism effects.

## Design Philosophy

This site embraces **modern minimalism** with a focus on **readability, whitespace, and subtle interactions**. The design is professional, clean, and accessible while maintaining visual appeal through refined colors, smooth animations, and thoughtful card design.

## Key Features

- **Frontend**: Next.js with TypeScript, Tailwind CSS, Framer Motion smooth animations, React Three Fiber 3D elements
- **Backend**: FastAPI with SQLAlchemy, SQLite database, REST API endpoints
- **Design**: Dark charcoal (#121212) theme with warm gold primary (#FFC857) and muted blue secondary (#5A7D9A)
- **Sections**: Hero with subtle 3D animations, About, Services, Portfolio, Testimonials, Contact
- **Typography**: Inter (body) + professional hierarchy with 1.7 line-height for readability
- **Animations**: Smooth fade-ins, scale-ins, and gentle transitions (no heavy glows)
- **Cards**: Glassmorphism with subtle blur (10px) and soft shadows for depth

## Design System

### Color Palette
- **Background**: #121212 (Dark charcoal) with subtle gradient to #1a1a1a
- **Primary Accent**: #FFC857 (Warm gold) - used for CTA buttons and key highlights
- **Secondary Accent**: #5A7D9A (Muted blue) - used for secondary elements
- **Text Primary**: #E0E0E0 (Off-white) - body text, reduced eye strain
- **Text Secondary**: #A0A0A0 (Muted gray) - secondary text, supporting info
- **Background Overlay**: rgba(255, 255, 255, 0.05) for card transparency

### Typography
- **Headings**: Inter Semi-Bold (600 weight), 14px line-height
- **Body Text**: Inter Regular (400 weight), 17px line-height, 0.2px letter-spacing
- **Monospace**: Roboto Mono for code snippets (reserved)

### Components
- **Cards**: Semi-transparent (5% opacity) with backdrop blur (10px), rounded corners (12px), subtle shadows
- **Buttons**: Solid colors (primary/secondary), pill-shaped (9999px radius), smooth hover animations
- **Spacing**: Generous padding (p-8 to p-10), increased gaps (gap-8 to gap-10) between elements
- **Shadows**: Soft, minimal shadows for subtle depth without heaviness

### Animations
- **Fade-in**: 0.6s ease-out (entrance animations for sections)
- **Scale-in**: 0.5s ease-out (card introductions)
- **Slide-up**: 0.6s ease-out (text block animations)
- **Float**: 2s ease-in-out infinite (gentle 3D element movement)
- **No glows**: Removed heavy text/box glows for modern aesthetic

## Getting Started

### Frontend

1. Install dependencies:
```bash
npm install
```

2. Run the development server:
```bash
npm run dev
```

Open [http://localhost:3000](http://localhost:3000) to view the website.

### Backend

1. Navigate to backend directory:
```bash
cd ../backend
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Initialize database:
```bash
python init_db.py
```

4. Run the API server:
```bash
python -m uvicorn main:app --reload
```

The API will be available at [http://localhost:8000](http://localhost:8000).
API documentation (Swagger UI): [http://localhost:8000/docs](http://localhost:8000/docs)

## Development Tips

### Customizing Colors
Edit CSS variables in `app/globals.css` (`:root` section):
```css
--accent-primary: #FFC857;      /* Change primary button/accent color */
--accent-secondary: #5A7D9A;    /* Change secondary accent */
--foreground: #E0E0E0;          /* Change text color */
```

### Modifying Animations
Update animation timings in `app/globals.css` (@keyframes section) or via Tailwind config (`tailwind.config.ts`).

### Adding New Sections
1. Create a new component in `app/components/`
2. Use the `.card` class for styled cards
3. Apply `.fade-in`, `.scale-in`, or `.slide-up` for animations
4. Maintain consistent padding (p-8 to p-10) and gaps (gap-8 to gap-10)

### Building for Production
```bash
npm run build
npm start
```

## API Endpoints

- GET/POST `/api/v1/services` - Manage services
- GET/POST `/api/v1/portfolios` - Manage portfolio items
- GET/POST `/api/v1/testimonials` - Manage testimonials
- GET/POST `/api/v1/contacts` - Manage contact form submissions

## Technologies Used

- **Frontend**: Next.js 16.2+, TypeScript, Tailwind CSS, Framer Motion, React Three Fiber
- **Backend**: FastAPI, SQLAlchemy ORM, SQLite
- **Fonts**: Inter (primary), Roboto Mono (monospace)
- **Styling**: CSS custom properties, Tailwind utilities, responsive design
- **Animations**: Framer Motion for smooth, performant transitions

## Project Structure

```
it-company-website/
├── app/
│   ├── components/          # React components (Hero, About, Services, etc.)
│   ├── globals.css          # Global styles, color variables, animations
│   ├── layout.tsx           # Root layout with font imports
│   └── page.tsx             # Homepage
├── tailwind.config.ts       # Tailwind configuration with custom colors
├── public/                  # Static assets
└── README.md               # This file

backend/
├── main.py                 # FastAPI app
├── models.py              # SQLAlchemy models
├── routes.py              # API endpoints
├── database.py            # Database configuration
└── requirements.txt       # Python dependencies
```

## Responsive Design

The site is fully responsive with:
- Mobile-first approach
- Large, accessible touch targets (min 48px)
- Responsive font sizing (base 16px mobile → scaled up on tablet/desktop)
- Flexible grid layouts (1 col mobile → 2-3 cols desktop)
- Scaled images and adaptable spacing

## Deployment

- **Frontend**: Deploy to Vercel, Netlify, or any Node.js hosting
- **Backend**: Deploy to Heroku, Railway, Render, or any Python hosting service

## Performance & Accessibility

✅ **Accessibility Features**
- WCAG AA color contrast compliance
- Semantic HTML structure
- Keyboard navigation support
- Smooth scrolling behavior
- Large touch targets (48px minimum)
- Clear focus states on interactive elements

✅ **Performance Optimizations**
- Optimized animations (GPU-accelerated)
- Lazy loading for images and components
- Minimal CSS kilobytes (Tailwind tree-shaking)
- Next.js image optimization
- Production build optimized (8-12s build time)

## Known Issues & Notes

⚠️ **THREE.Clock Deprecation Warning**
- **Issue**: Browser console shows "THREE.THREE.Clock: This module has been deprecated. Please use THREE.Timer instead"
- **Cause**: React Three Fiber library internally uses THREE.Clock, which has been deprecated in THREE.js v0.183+
- **Impact**: Harmless warning - functionality works perfectly, no user-facing issues
- **Resolution**: This will be fixed when React Three Fiber updates their internal code to use THREE.Timer
- **Workaround**: Warning can be safely ignored as it doesn't affect performance or functionality

## Contributing

To contribute or customize:
1. Fork/clone the repo
2. Install dependencies (`npm install` for frontend, `pip install -r requirements.txt` for backend)
3. Create a new branch
4. Make changes
5. Test locally (`npm run dev` and `uvicorn main:app --reload`)
6. Submit a PR

## License

MIT License - Feel free to use this project for your own IT company or portfolio.
