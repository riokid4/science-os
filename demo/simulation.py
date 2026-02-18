"""Auto-generated Science OS Simulation"""
import numpy as np
from scipy.integrate import odeint
import matplotlib.pyplot as plt

# Species: 4
# Reactions: 3

def get_initial_conditions():
    return np.ones(4)

def ode_system(y, t):
    dydt = np.zeros(4)
    dydt[1] -= 0.1 * y[0] * y[1]  # phosphorylation
    dydt[2] += 0.1 * y[1]  # activation
    dydt[1] -= 0.05 * y[3]  # inhibition
    return dydt

def run_simulation():
    print("Running p53 pathway simulation...")
    y0 = get_initial_conditions()
    t = np.linspace(0, 100, 1000)
    sol = odeint(ode_system, y0, t)
    
    plt.figure(figsize=(10, 6))
    plt.plot(t, sol[:, 0], label="q13315")
    plt.plot(t, sol[:, 1], label="p04637")
    plt.plot(t, sol[:, 2], label="p38936")
    plt.plot(t, sol[:, 3], label="q00987")
    plt.xlabel("Time")
    plt.ylabel("Concentration")
    plt.title("Science OS - p53 Signaling")
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.savefig("p53_simulation.png", dpi=150)
    print("✓ Done! Saved to p53_simulation.png")

if __name__ == "__main__":
    run_simulation()