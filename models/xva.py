"""
All functions return dicts; all CVA/DVA/FVA/MVA scalars are POSITIVE (costs/benefits).
"""
import numpy as np


# Credit helpers

def hazard_rate(cds_spread_bps: float, lgd: float) -> float:
    return (cds_spread_bps / 10_000) / lgd


def survival_prob(t: np.ndarray, lam: float) -> np.ndarray:
    return np.exp(-lam * t)


def cumulative_pd(t: np.ndarray, lam: float) -> np.ndarray:
    return 1.0 - survival_prob(t, lam)


def marginal_pd(t: np.ndarray, lam: float) -> np.ndarray:
    return np.diff(cumulative_pd(t, lam))


def discount_factors(t: np.ndarray, r: float) -> np.ndarray:
    return np.exp(-r * t)


# CVA — Credit Valuation Adjustment

def calculate_cva(
    EE: np.ndarray,
    t: np.ndarray,
    cds_spread_bps: float,
    recovery: float,
    risk_free_rate: float,
) -> dict:
    """
    CVA = Σᵢ DF(tᵢ) · ΔPD_cp(tᵢ) · LGD · EE(tᵢ)
    Returns CVA as a POSITIVE cost
    """
    lgd = 1.0 - recovery
    lam = hazard_rate(cds_spread_bps, lgd)
    marg_pd_ = marginal_pd(t, lam)
    t_mid = 0.5 * (t[:-1] + t[1:])
    df = discount_factors(t_mid, risk_free_rate)
    ee_mid = 0.5 * (EE[:-1] + EE[1:])

    contributions = df * marg_pd_ * lgd * ee_mid
    cva_cost = float(np.sum(contributions))

    return {
        "CVA": cva_cost,
        "contributions": contributions,
        "t_mid": t_mid,
        "marg_pd": marg_pd_,
        "ee_mid": ee_mid,
        "lgd": lgd,
        "hazard_rate": lam,
    }


# DVA — Debit Valuation Adjustment

def calculate_dva(
    ENE: np.ndarray,
    t: np.ndarray,
    own_cds_spread_bps: float,
    own_recovery: float,
    risk_free_rate: float,
) -> dict:
    """
    DVA = Σᵢ DF(tᵢ) · ΔPD_bank(tᵢ) · LGD_bank · ENE(tᵢ)
    Returns DVA as a POSITIVE benefit
    """
    own_lgd = 1.0 - own_recovery
    lam_bank = hazard_rate(own_cds_spread_bps, own_lgd)
    marg_pd_bank = marginal_pd(t, lam_bank)
    t_mid = 0.5 * (t[:-1] + t[1:])
    df = discount_factors(t_mid, risk_free_rate)
    ene_mid = 0.5 * (ENE[:-1] + ENE[1:])

    contributions = df * marg_pd_bank * own_lgd * ene_mid
    dva_benefit = float(np.sum(contributions))

    return {
        "DVA": dva_benefit,
        "contributions": contributions,
        "t_mid": t_mid,
        "marg_pd": marg_pd_bank,
        "ene_mid": ene_mid,
        "lgd": own_lgd,
        "hazard_rate": lam_bank,
    }


# FVA — Funding Valuation Adjustment

def calculate_fva(
    EE: np.ndarray,
    t: np.ndarray,
    funding_spread_bps: float,
    risk_free_rate: float,
) -> dict:
    """
    FVA = Σᵢ DF(tᵢ) · s_f · EE(tᵢ) · Δt
    Returns FVA as a POSITIVE cost.
    """
    spread = funding_spread_bps / 10_000
    t_mid = 0.5 * (t[:-1] + t[1:])
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
        "spread": spread,
    }


# MVA — Margin Valuation Adjustment

def calculate_mva(
    notional: float,
    exposure_vol: float,
    t: np.ndarray,
    funding_spread_bps: float,
    risk_free_rate: float,
    mpor_days: int = 10,
    init_margin_dollars: float = 0.0,
    z_99: float = 2.326,
) -> dict:
    """
    IM = manual if > 0, else z₉₉ · σ · N · √(MPOR/252)
    MVA = Σᵢ DF(tᵢ) · s_f · IM · Δt
    Returns MVA as a POSITIVE cost.
    """
    if init_margin_dollars > 0:
        im = init_margin_dollars
        source = "manual"
    else:
        im = z_99 * exposure_vol * notional * np.sqrt(mpor_days / 252)
        source = "estimated"

    spread = funding_spread_bps / 10_000
    t_mid = 0.5 * (t[:-1] + t[1:])
    dt = np.diff(t)
    df = discount_factors(t_mid, risk_free_rate)

    contributions = df * spread * im * dt
    mva_cost = float(np.sum(contributions))

    return {
        "MVA": mva_cost,
        "contributions": contributions,
        "t_mid": t_mid,
        "im": im,
        "im_source": source,
        "dt": dt,
        "spread": spread,
    }


# Total XVA

def total_xva(cva: float, dva: float, fva: float, mva: float) -> float:
    """Total XVA Cost = CVA - DVA + FVA + MVA  (all inputs are positive scalars)."""
    return cva - dva + fva + mva
