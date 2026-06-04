"""
models/simulation.py — GBM MtM exposure simulation
"""
import numpy as np


def simulate_exposure(
    notional: float,
    current_mtm: float,
    vol: float,
    maturity: float,
    n_steps: int,
    n_scenarios: int,
    risk_free_rate: float,
    collateralized: bool = False,
    seed: int = 42,
) -> dict:
    rng = np.random.default_rng(seed)
    dt = maturity / n_steps
    t = np.linspace(0, maturity, n_steps + 1)
    Z = rng.standard_normal((n_scenarios, n_steps))

    # Geometric Brownian Motion: dMtM = r*MtM*dt + vol*MtM*dW
    drift = (risk_free_rate - 0.5 * vol**2) * dt
    diffusion = vol * np.sqrt(dt)
    mtm0 = current_mtm / notional
    log_paths = np.cumsum(drift + diffusion * Z, axis=1)
    col0 = np.full((n_scenarios, 1), mtm0)
    mtm_paths = np.concatenate(
        [col0, mtm0 * np.exp(log_paths)], axis=1) * notional

    cf = 0.5 if collateralized else 1.0
    exposure_pos = np.maximum(mtm_paths,  0) * cf
    exposure_neg = np.maximum(-mtm_paths, 0) * cf

    EE = exposure_pos.mean(axis=0)
    ENE = exposure_neg.mean(axis=0)
    PFE95 = np.percentile(exposure_pos, 95, axis=0)
    PFE99 = np.percentile(exposure_pos, 99, axis=0)

    return {
        "t": t, "EE": EE, "ENE": ENE,
        "PFE95": PFE95, "PFE99": PFE99,
        "mtm_paths": mtm_paths,
        "exposure_pos": exposure_pos,
        "exposure_neg": exposure_neg,
    }
