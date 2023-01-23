# =============================================================================
# Acceleration spectra for a given accelerogram through Newmark Algorithm
# =============================================================================
import numpy as np

def diferencia_centrada(Tn,xi,DDug,dt):
    # Parámetros de la estructura
    m = 1
    wn = 2 * np.pi / Tn
    k = wn**2 * m 
    c = 2 * xi * wn * m
    
    # Para evitar inestabilidad, se ajustan los datos si dt es grande 
    while dt > Tn / 10:
        N = len(DDug)
        t1 = np.array(range(1,N+1,1))
        t2 = np.linspace(1,N,2*N-1)
        DDug = np.interp(t2,t1,DDug)
        dt = dt/2
    
    # Se prealojan los datos
    N   = np.size(DDug)
    u   = np.zeros((1,N+1))
    Du  = np.zeros((1,N))
    DDu = np.zeros((1,N))
    
    # Por comodidad se construye el vector de excitación
    p = -1 * m * DDug
    
    # Cálculos iniciales
    kt = m / dt**2 + c / (2 * dt)
    a  = m / dt**2 - c / (2 * dt)
    b  = k - 2 * m / dt**2
    
    # Cálculo en primera iteración
    i = 0
    DDu[0,i] = (p[0,i] - c*Du[0,i] - k*u[0,i]) / m
    um1 = u[0,i] - dt * Du[0,i] + dt**2 / 2 * DDu[0,i]
    pt0 = p[0,i] - a * um1 - b * u[0,i]
    u[0,i+1] = pt0 / kt
    
    # Iteraciones
    for i in range(1,N):
        pti = p[0,i] - a * u[0, i-1] - b * u[0,i];
        u[0,i+1] = pti / kt;
        # Du[i]  = (u[i+1] - u[i-1]) / (2*dt);
        # DDu[i] = (u[i+1] - 2*u[i] + u[i-1]) / dt**2;
    
    # Se elimina el último dato del vector de desplazamientos para que tenga igual longitud
    u = u[0,0:-1].reshape((1,N))
    
    return u
    
    
def getSa(T,xi,DDug,dt):
        u = diferencia_centrada(T,xi,DDug,dt)
        Sa = np.amax(np.absolute(u)) * (2*np.pi/T)**2
        return Sa

