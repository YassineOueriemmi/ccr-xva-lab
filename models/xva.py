
import numpy as np


# Credit helpers

def hazard_rate(cds_spread_bps: float, lgd: float) -> float:  # = CDS spread / LGD
    return (cds_spread_bps / 10000) / lgd


def survival_prob(t: np.ndarray, lam: float) -> np.ndarray:  # = e^(−λ·t)
    return np.exp(-lam * t)


def cumulative_pd(t: np.ndarray, lam: float) -> np.ndarray:  # = 1 − e^(−λ·t)
    return 1.0 - survival_prob(t, lam)


def marginal_pd(t: np.ndarray, lam: float) -> np.ndarray:  # = Q(tᵢ) − Q(tᵢ₋₁)
    return np.diff(cumulative_pd(t, lam))


def discount_factors(t: np.ndarray, r: float) -> np.ndarray:  # = e^(−r·t)
    return np.exp(-r * t)


# CVA = Σᵢ DF(tᵢ) * ΔPD_cp(tᵢ) * LGD * EE(tᵢ)

def calculate_cva(
        EE: np.ndarray,
        t: np.ndarray,
        cds_spread_bps: float,
        recovery: float,
        risk_free_rate: float) -> dict:

    lgd = 1.0 - recovery
    lam = hazard_rate(cds_spread_bps, lgd)
    marg_pd_ = marginal_pd(t, lam)
    # On utilise le mid de l'intervalle de proba de default, psk on suppose qu'il arrive au milieu
    t_mid = 0.5 * (t[:-1] + t[1:])
    df = discount_factors(t_mid, risk_free_rate)
    ee_mid = 0.5 * (EE[:-1] + EE[1:])  # interpolation linéaire

    contributions = df * marg_pd_ * lgd * ee_mid
    cva_cost = float(np.sum(contributions))

    return {
        "CVA": cva_cost,
        "contributions": contributions,
        "t_mid": t_mid,
        "marg_pd": marg_pd_,
        "ee_mid": ee_mid,
        "lgd": lgd,
        "hazard_rate": lam}


# FVA = Σᵢ DF(tᵢ) * spread_funding * EE(tᵢ) * Δt

def calculate_fva(
        EE: np.ndarray,
        t: np.ndarray,
        funding_spread_bps: float,
        risk_free_rate: float) -> dict:

    spread = funding_spread_bps / 10000
    t_mid = 0.5 * (t[:-1] + t[1:])  # millieu de l'interval comme pour le CVA
    # Le coût de financement s'accumule proportionnellement au temps
    dt = np.diff(t)
    df = discount_factors(t_mid, risk_free_rate)
    ee_mid = 0.5 * (EE[:-1] + EE[1:])

    contributions = df * spread * ee_mid * dt
    fva_cost = float(np.sum(contributions))

    return {
        "FVA": fva_cost,
        "contributions": contributions,
        "t_mid": t_mid,
        "ee_mid": ee_mid,
        "dt": dt,
        "spread": spread}


#  MVA = Σᵢ DF(tᵢ) * s_f * IM * Δt

def calculate_mva(
        init_margin_dollars: float,
        t: np.ndarray,
        funding_spread_bps: float,
        risk_free_rate: float) -> dict:

    spread = funding_spread_bps / 10000
    t_mid = 0.5 * (t[:-1] + t[1:])
    dt = np.diff(t)
    df = discount_factors(t_mid, risk_free_rate)

    contributions = df * spread * init_margin_dollars * \
        dt  # cout de financer l'IM sur chaque delta t
    mva_cost = float(np.sum(contributions))

    return {
        "MVA":           mva_cost,
        "contributions": contributions,
        "t_mid":         t_mid,
        "im":            init_margin_dollars,
        "spread":        spread}

