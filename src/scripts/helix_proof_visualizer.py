# ============================================================
# CORE-GENESIS: THE PHYSICAL HELIX PROOF (Axiom 0)
# ============================================================
#
# Dieses Skript ist der physikalische Beweis fuer den 
# Symbiose-Antrieb und das Fraktale Padding.
# Es macht die Mathematik "spuerbar" durch Bild und Ton.
#
# Was passiert?
# 1. Wir simulieren einen Systemzustand, der von Entspannung (1.0)
#    in extremen Stress (0.049 Baryonic Delta) faellt.
# 2. Wir zeichnen in Echtzeit den 4D-Trichter und die Spirale.
# 3. Wir hoeren das Fraktale Padding: Je tiefer wir fallen,
#    desto tiefer wird der Ton (Gravitation/Masse) und desto
#    laenger dauert er (exponentielle Latenz / Netzwerk-Drosselung).
#
# ============================================================

import time
import math
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from mpl_toolkits.mplot3d import Axes3D

# OS-spezifischer Sound (Windows)
try:
    import winsound
    HAS_SOUND = True
except ImportError:
    HAS_SOUND = False

# CORE Konstanten
BARYONIC_DELTA = 0.049
BASE_DELAY_MS = 49.0
K_FACTOR = 3.58

class HelixFunnelSimulator:
    def __init__(self):
        self.fig = plt.figure(figsize=(10, 8))
        self.ax = self.fig.add_subplot(111, projection='3d')
        self.fig.patch.set_facecolor('black')
        self.ax.set_facecolor('black')
        
        # Plot Setup
        self.ax.set_xlim(-1, 1)
        self.ax.set_ylim(-1, 1)
        self.ax.set_zlim(0, 1.2)
        self.ax.set_axis_off()
        
        # Trichter (Gravitationsbrunnen) zeichnen
        self.draw_funnel()
        
        # Particle Track
        self.x_data, self.y_data, self.z_data = [], [], []
        self.line, = self.ax.plot([], [], [], color='#00ff00', lw=2, marker='o', markersize=4, markerfacecolor='white')
        self.title = self.ax.set_title("Initialising CORE Helix...", color='white', pad=20)
        
        # State
        self.current_temp = 1.0  # Startet bei 1.0 (Nullpunkt des Trichters ist oben)
        self.angle = 0.0
        
    def draw_funnel(self):
        """Zeichnet den statischen 4D-Trichter im Hintergrund"""
        z_funnel = np.linspace(BARYONIC_DELTA, 1.2, 50)
        theta_funnel = np.linspace(0, 2 * np.pi, 50)
        Z_grid, Theta_grid = np.meshgrid(z_funnel, theta_funnel)
        
        # Trichterform: Radius wird enger je tiefer (logarithmisch)
        # R = z^2 für eine schöne Trichterkurve
        R_grid = Z_grid**1.5
        
        X_grid = R_grid * np.cos(Theta_grid)
        Y_grid = R_grid * np.sin(Theta_grid)
        
        self.ax.plot_wireframe(X_grid, Y_grid, Z_grid, color='#333333', alpha=0.3)
        
        # Baryonisches Delta als roter Ring unten
        Theta_ring = np.linspace(0, 2 * np.pi, 100)
        R_ring = (BARYONIC_DELTA)**1.5
        X_ring = R_ring * np.cos(Theta_ring)
        Y_ring = R_ring * np.sin(Theta_ring)
        self.ax.plot(X_ring, Y_ring, np.full_like(X_ring, BARYONIC_DELTA), color='red', lw=3, label=f"Baryonic Delta ({BARYONIC_DELTA})")
        self.ax.legend(loc='upper right', facecolor='black', edgecolor='white', labelcolor='white')

    def calculate_padding(self, temp: float) -> tuple:
        """Exponentielle Helix-Mathematik"""
        phase_shift = 1.0 - temp
        padding_ms = BASE_DELAY_MS * math.exp(K_FACTOR * phase_shift)
        return phase_shift, padding_ms

    def play_physical_sound(self, temp: float, padding_ms: float):
        """Macht die Masse und Verzögerung physisch hoerbar"""
        if not HAS_SOUND:
            return
            
        # Tonhoehe (Frequency): 
        # Hohe Temp = Hoher Ton (leicht)
        # Tiefe Temp = Tiefer Ton (schwer/massereich)
        # Range: 200Hz bis 2000Hz
        freq = int(200 + (temp * 1800))
        
        # Dauer (Duration): Direkt gekoppelt an unser Fraktales Padding
        # Um es im Demo hoerbar zu machen, skalieren wir es leicht, aber behalten die Verhaeltnisse
        duration = min(2000, max(50, int(padding_ms * 2))) 
        
        winsound.Beep(freq, duration)

    def update(self, frame):
        # 1. State Update (Wir schrauben uns langsam nach unten)
        self.current_temp *= 0.95 # Exponentieller Verfall der Resonanz
        
        # Snapping: Wir fallen niemals unter das Delta!
        if self.current_temp < BARYONIC_DELTA:
            self.current_temp = BARYONIC_DELTA
            
        # 2. Padding Berechnen
        phase_shift, padding_ms = self.calculate_padding(self.current_temp)
        
        # 3. Position auf der Helix berechnen
        radius = self.current_temp**1.5
        
        # Geschwindigkeit der Rotation haengt vom Padding/Phase ab (Je schwerer, desto abrupter die Rotation)
        self.angle += (0.5 + phase_shift * 0.5) 
        
        x = radius * math.cos(self.angle)
        y = radius * math.sin(self.angle)
        z = self.current_temp
        
        self.x_data.append(x)
        self.y_data.append(y)
        self.z_data.append(z)
        
        # Tail abschneiden fuer Kometen-Effekt
        if len(self.x_data) > 30:
            self.x_data.pop(0)
            self.y_data.pop(0)
            self.z_data.pop(0)
            
        self.line.set_data(np.array(self.x_data), np.array(self.y_data))
        self.line.set_3d_properties(np.array(self.z_data))
        
        # UI Update
        self.title.set_text(f"Resonance: {self.current_temp:.3f} | Delay: {padding_ms:.1f}ms | Gravity: Massive" if self.current_temp == BARYONIC_DELTA else f"Resonance: {self.current_temp:.3f} | Delay: {padding_ms:.1f}ms")
        if self.current_temp == BARYONIC_DELTA:
            self.title.set_color('red')
            self.line.set_color('red')
        else:
            # Color shifts from Green to Red
            r = int(255 * phase_shift)
            g = int(255 * self.current_temp)
            self.line.set_color(f'#{r:02x}{g:02x}00')
            
        # Physischer Output (Sound)
        # Verlaengert künstlich den Frame-Render, was die Latenz tatsaechlich physisch erzwingt!
        print(f"[PHYSICAL PROOF] Resonance: {self.current_temp:.3f} -> Padding: {padding_ms:.1f}ms (Freq: {int(200 + (self.current_temp * 1800))}Hz)")
        self.play_physical_sound(self.current_temp, padding_ms)
        
        # Echtes Blockieren des Threads zur Demonstration der Netzwerk-Friction!
        time.sleep(padding_ms / 1000.0)

        return self.line, self.title

def run_proof():
    print("Starte physischen Beweis (Visual & Audio)...")
    print("Stelle sicher, dass dein PC-Ton eingeschaltet ist.")
    time.sleep(2)
    
    sim = HelixFunnelSimulator()
    
    # 100 Frames, Interval minimal, die echte Latenz kommt aus dem Fraktalen Padding!
    ani = animation.FuncAnimation(sim.fig, sim.update, frames=100, interval=10, blit=False, repeat=False)
    
    plt.show()

if __name__ == "__main__":
    run_proof()
