import { useCallback, useEffect, useRef, useState } from "react";
import type { ReactNode } from "react";
import { AnimatePresence, motion, useInView, useReducedMotion, useScroll, useTransform } from "motion/react";
import {
  ArrowDown,
  ArrowRight,
  ArrowUpRight,
  Compass,
  Network,
  ScanSearch,
  Sparkles,
} from "lucide-react";

/* Where each way in lands. The atlas reads its own view from the fragment, so
   the landing can hand a reader straight to the part it was just describing
   rather than dropping everyone on the overview. */
const ATLAS_SRC = "/atlas/index.html";
type AtlasView = "atlas" | "find" | "directory" | "graph" | "notes";

const stations = [
  {
    view: "atlas" as AtlasView,
    title: "Read the field",
    text: "See Emory’s research landscape as a living spectrum, from wet bench to dry computation.",
    cue: "Overview",
    icon: Compass,
    accent: "coral",
  },
  {
    view: "find" as AtlasView,
    title: "Find your people",
    text: "Search by topic, method, place, or name. The Atlas turns an enormous directory into a starting point.",
    cue: "Search",
    icon: ScanSearch,
    accent: "blue",
  },
  {
    view: "graph" as AtlasView,
    title: "Follow the links",
    text: "Move through shared grants, papers, departments, and first-degree relationships in the network graph.",
    cue: "Graph",
    icon: Network,
    accent: "violet",
  },
];

function Reveal({ children, delay = 0, className = "" }: { children: ReactNode; delay?: number; className?: string }) {
  const ref = useRef<HTMLDivElement | null>(null);
  const inView = useInView(ref, { once: true, margin: "-12% 0px" });
  return (
    <motion.div
      ref={ref}
      className={className}
      initial={{ opacity: 0, y: 28 }}
      animate={inView ? { opacity: 1, y: 0 } : undefined}
      transition={{ duration: 0.72, delay, ease: [0.22, 1, 0.36, 1] }}
    >
      {children}
    </motion.div>
  );
}

function Grain() {
  return <div className="grain" aria-hidden="true" />;
}

type Origin = { x: number; y: number; w: number; h: number };

export default function Home() {
  const [atlas, setAtlas] = useState<{ view: AtlasView; from: Origin | null } | null>(null);
  const [expanded, setExpanded] = useState(false);
  const reduce = useReducedMotion();
  const heroRef = useRef<HTMLElement | null>(null);
  const atlasOpen = atlas !== null;

  /* One way in, used by every affordance on the page. It measures whatever was
     clicked and hands that rectangle to the overlay, which grows out of it, so
     the atlas arrives from the thing you pressed rather than replacing the page
     underneath you. Falls back to the centre of the screen for a keyboard press
     or anything with no sensible rectangle. */
  const openAtlas = useCallback((view: AtlasView, event?: { currentTarget: Element | null }) => {
    const node = event?.currentTarget as HTMLElement | null;
    const r = node?.getBoundingClientRect?.();
    setAtlas({
      view,
      from: r && r.width > 0 ? { x: r.left, y: r.top, w: r.width, h: r.height } : null,
    });
    setExpanded(false);
  }, []);

  const closeAtlas = useCallback(() => {
    setExpanded(false);
    setAtlas(null);
  }, []);

  // the overlay starts at the source rectangle and then releases to full size on
  // the next frame, so the growth is a transition rather than a jump
  useEffect(() => {
    if (!atlasOpen) return;
    if (reduce) { setExpanded(true); return; }
    const id = requestAnimationFrame(() => requestAnimationFrame(() => setExpanded(true)));
    return () => cancelAnimationFrame(id);
  }, [atlasOpen, reduce]);
  const { scrollYProgress } = useScroll();
  const heroY = useTransform(scrollYProgress, [0, 0.22], [0, -90]);
  const orbY = useTransform(scrollYProgress, [0, 0.4], [0, 190]);

  useEffect(() => {
    const previous = document.body.style.overflow;
    if (atlasOpen) document.body.style.overflow = "hidden";
    return () => {
      document.body.style.overflow = previous;
    };
  }, [atlasOpen]);

  useEffect(() => {
    const onKeyDown = (event: KeyboardEvent) => {
      if (event.key === "Escape") closeAtlas();
    };
    window.addEventListener("keydown", onKeyDown);
    return () => window.removeEventListener("keydown", onKeyDown);
  }, [closeAtlas]);

  return (
    <div className="landing-shell">
      <Grain />
      <header className="landing-nav">
        <a className="brand-lockup" href="#top" aria-label="Emory Lab Atlas home">
          <span className="brand-mark">E</span>
          <span>
            <strong>Emory Lab Atlas</strong>
            <small>Research, mapped.</small>
          </span>
        </a>
        <nav className="nav-links" aria-label="Primary navigation">
          <a href="#method">How it works</a>
          <a href="#atlas">The Atlas</a>
          <a href="#about">About</a>
        </nav>
        <button className="nav-cta" onClick={(e) => openAtlas("atlas", e)}>
          Enter Atlas <ArrowUpRight size={15} />
        </button>
      </header>

      <main id="top">
        <section ref={heroRef} className="hero-section">
          <motion.div className="hero-orbit hero-orbit-one" style={{ y: orbY }} />
          <motion.div className="hero-orbit hero-orbit-two" style={{ y: orbY }} />
          <motion.div className="hero-content" style={{ y: heroY }}>
            <Reveal className="eyebrow-row">
              <span className="eyebrow-dot" />
              <span>Emory University</span>
            </Reveal>
            <Reveal delay={0.08}>
              <h1>
                Every lab is a <em>world.</em>
                <br />
                Start with the map.
              </h1>
            </Reveal>
            <Reveal delay={0.16}>
              <p className="hero-lede">
                A visual index of Emory’s investigators, departments, topics, and connections. Built to help you find the next question, collaborator, or place to begin.
              </p>
            </Reveal>
            <Reveal delay={0.24} className="hero-actions">
              <button className="button-primary" onClick={(e) => openAtlas("atlas", e)}>
                Explore the Atlas <ArrowRight size={17} />
              </button>
              <a className="button-secondary" href="#method">
                See how it works <ArrowDown size={16} />
              </a>
            </Reveal>
            <Reveal delay={0.32} className="hero-footnote">
              <span>7,089 investigators</span>
              <i />
              <span>107 departments & centers</span>
              <i />
              <span>One navigable field</span>
            </Reveal>
          </motion.div>
          <div className="hero-visual">
            <div className="visual-label visual-label-left">wet bench</div>
            <div className="visual-label visual-label-right">dry computation</div>
            <div className="axis-line">
              <span className="axis-node node-one" />
              <span className="axis-node node-two" />
              <span className="axis-node node-three" />
              <span className="axis-node node-four" />
            </div>
            <button type="button" className="hero-card hero-card-main" onClick={(e) => openAtlas("atlas", e)} aria-label="Open the atlas overview">
              <div className="mini-card-top"><span>Live field note</span><span>inferred</span></div>
              <div className="mini-spectrum"><span /><span /><span /><span /><span /></div>
              <div className="mini-card-bottom"><strong>Research settings</strong><span>inferred from records</span></div>
            </button>
            <button type="button" className="hero-card hero-card-float" onClick={(e) => openAtlas("graph", e)} aria-label="Open the atlas graph">
              <div className="float-icon"><Network size={17} /></div>
              <div><strong>First-degree ties</strong><span>shared topics, grants, papers</span></div>
            </button>
          </div>
        </section>

        <section id="method" className="method-section section-pad">
          <Reveal className="section-intro">
            <span className="section-kicker">A better starting point</span>
            <h2>Not another directory.<br /><em>A way into the work.</em></h2>
            <p>Research is not a list. It is a field of adjacent questions, methods, people, and places. The Atlas gives you enough shape to move through it with intention.</p>
          </Reveal>
          <div className="stations-grid">
            {stations.map((station, index) => {
              const Icon = station.icon;
              return (
                <Reveal key={station.view} delay={index * 0.08}>
                  <button
                    type="button"
                    className={`station-card station-${station.accent}`}
                    onClick={(e) => openAtlas(station.view, e)}
                    aria-label={`Open the atlas: ${station.title}`}
                  >
                    <div className="station-top"><span>{station.cue}</span><Icon size={20} strokeWidth={1.6} /></div>
                    <div><h3>{station.title}</h3><p>{station.text}</p></div>
                    <span className="station-arrow"><ArrowUpRight size={16} /></span>
                  </button>
                </Reveal>
              );
            })}
          </div>
        </section>

        <section id="atlas" className="atlas-teaser-section section-pad">
          <Reveal className="atlas-kicker"><span className="section-kicker">The living interface</span><span className="atlas-kicker-line" /></Reveal>
          <Reveal delay={0.08} className="atlas-teaser-copy">
            <div><h2>The whole field,<br /><em>one axis.</em></h2></div>
            <div><p>Begin with the overview, then zoom into a lab, a department, or a relationship. The Atlas keeps the big picture present while you go deep.</p><button className="text-link" onClick={(e) => openAtlas("atlas", e)}>Open the full Atlas <ArrowRight size={15} /></button></div>
          </Reveal>
          <Reveal delay={0.16} className="atlas-window-wrap">
            <button className="atlas-window" onClick={(e) => openAtlas("atlas", e)} aria-label="Open the interactive Atlas">
              <div className="window-bar"><span className="window-dots"><i /><i /><i /></span><span>emory.lab.atlas / overview</span><span className="window-status"><span /> live index</span></div>
              <div className="window-body">
                <div className="window-rail"><span className="rail-active">Atlas</span><span>Find a lab</span><span>Directory</span><span>Graph</span><span>Notes</span></div>
                <div className="window-main"><span className="window-eyebrow">Emory University</span><strong>Every lab at Emory,<br />on one <b>axis.</b></strong><div className="window-copy">7,089 investigators across 107 departments and centers</div><div className="window-wave"><span /><span /><span /></div><div className="window-legend"><span>wet bench</span><span>2,977 placed</span><span>dry & computational</span></div></div>
              </div>
              <div className="window-hint"><Sparkles size={14} /> Click anywhere to enter the atlas</div>
            </button>
          </Reveal>
        </section>

        <section id="about" className="closing-section section-pad">
          <Reveal className="closing-grid">
            <div><span className="section-kicker">A note on the map</span><h2>Useful, not definitive.</h2></div>
            <div><p>The Atlas reads what labs say about themselves. Wet, dry, and hybrid settings are predictions rather than records, and every path is an invitation to confirm, question, and keep looking.</p><button className="button-primary small" onClick={(e) => openAtlas("notes", e)}>Read the notes <ArrowRight size={16} /></button></div>
          </Reveal>
        </section>
      </main>

      <footer className="landing-footer"><span>Emory Lab Atlas</span><span>Built for orientation, discovery, and the next question.</span><a href="https://reactbits.dev/c/micro" target="_blank" rel="noreferrer">Motion layer by ReactBits <ArrowUpRight size={13} /></a></footer>

      <AnimatePresence>
        {atlas && (
          <motion.div
            className="atlas-overlay"
            initial={{ opacity: reduce ? 1 : 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            transition={{ duration: reduce ? 0 : 0.22 }}
          >
            {/* The growing panel. Only transform and opacity are animated: the
                panel is always full size and is scaled down to the rectangle of
                whatever was clicked, then released to identity. */}
            <div
              className={`atlas-panel${expanded ? " is-open" : ""}`}
              style={
                !expanded && atlas.from
                  ? {
                      transform: `translate(${atlas.from.x}px, ${atlas.from.y}px) scale(${
                        atlas.from.w / window.innerWidth
                      }, ${atlas.from.h / window.innerHeight})`,
                      opacity: 0.4,
                    }
                  : !expanded
                    ? { transform: "scale(.92)", opacity: 0 }
                    : undefined
              }
            >
              {/* the atlas carries its own masthead, so this bar says only the
                  one thing the atlas cannot: how to get back out */}
              <div className="atlas-bar">
                <span className="atlas-bar-name">Emory Lab Atlas</span>
                <button onClick={closeAtlas} aria-label="Close the atlas">
                  Back to the guide <span>Esc</span>
                </button>
              </div>
              <iframe
                src={`${ATLAS_SRC}#${atlas.view}`}
                title="Emory Lab Atlas"
                loading="eager"
              />
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}
