# Deterministic stress scenarios on CDS spread, recovery, and exposure volatility

import numpy as np
from .xva import calculate_cva


STRESS_SCENARIOS = {
    "Credit spread +50 bps":                    {"spread_add": 50,  "recovery_add": 0.0,   "vol_mult": 1.0},
    "Credit spread +100 bps":                   {"spread_add": 100, "recovery_add": 0.0,   "vol_mult": 1.0},
    "Credit spread +200 bps":                   {"spread_add": 200, "recovery_add": 0.0,   "vol_mult": 1.0},
    "Recovery rate −10%":                       {"spread_add": 0,   "recovery_add": -0.10, "vol_mult": 1.0},
    "Exposure vol +25%":                        {"spread_add": 0,   "recovery_add": 0.0,   "vol_mult": 1.25},
    "Combined (+100 bps, rec −10%, vol +25%)":  {"spread_add": 100, "recovery_add": -0.10, "vol_mult": 1.25}}


def run_stress_tests(
        EE_base: np.ndarray,
        t: np.ndarray,
        base_cds_bps: float,
        base_recovery: float,
        risk_free_rate: float) -> list:

    base_result = calculate_cva(
        EE_base, t, base_cds_bps, base_recovery, risk_free_rate)  # CVA réaliste
    base_cva_cost = base_result["CVA"]
    base_lgd = 1.0 - base_recovery
    base_lam = (base_cds_bps / 10_000) / base_lgd

    rows = []
    for name, scenario in STRESS_SCENARIOS.items():
        spread_add = scenario["spread_add"]
        recovery_add = scenario["recovery_add"]
        vol_mult = scenario["vol_mult"]

        # on borne la reco entre 0.01 et 0.99 pour éviter des valeurs absurdes
        stressed_recovery = max(0.01, min(0.99, base_recovery + recovery_add))

        if recovery_add != 0.0 and spread_add == 0:
            lgd_stressed = 1.0 - stressed_recovery
            # si notre LGD change notre cds spread doit changer psk λ = CDS / LGD
            effective_cds = base_lam * lgd_stressed * 10000
        else:
            effective_cds = base_cds_bps + spread_add

        # c'est un proxy psk l'EE est un gbm qui scales linearly avec la vol, ça avoids re-simulation (ça reste une approx)
        EE_stressed = EE_base * vol_mult

        res = calculate_cva(EE_stressed, t, effective_cds,
                            stressed_recovery, risk_free_rate)
        stressed_cva_cost = res["CVA"]
        delta = stressed_cva_cost - base_cva_cost
        # pour eviter de diviser par 0
        pct = (delta / base_cva_cost * 100) if base_cva_cost != 0 else 0.0

        rows.append({
            "Scenario":          name,
            "Stressed CVA Cost": stressed_cva_cost,
            "Base CVA Cost":     base_cva_cost,
            "Δ CVA Cost":        delta,
            "% Change":          pct})

    return rows

    """
    Monte Carlo CVA VaR via spread shocks
    Spread shock: σ_spread * sqrt(horizon/252) * Z,  Z ~ N(0,1)
    on simule 10 000 chocs de spread, on recalcule le CVA pour chacun, et on prend le percentile 99% de la distribution des pertes
    """


def simulate_cva_var(
        EE: np.ndarray,
        t: np.ndarray,
        base_cds_bps: float,
        recovery: float,
        risk_free_rate: float,
        spread_vol_bps: float = 60.0,
        horizon_days: int = 10,
        n_scenarios: int = 10000,
        seed: int = 42) -> dict:

    rng = np.random.default_rng(seed)
    Z = rng.standard_normal(n_scenarios)

    # on scale la vol annuel du spread sur notre time horizon
    spread_shock = spread_vol_bps * np.sqrt(horizon_days / 252.0) * Z
    # floor at 1 bp pour garantir que tous les spreads restent réalistes, pas de spreads négaitfs (on va pas nous payer pour nous assurer)
    stressed_spreads = np.maximum(base_cds_bps + spread_shock, 1.0)

    lgd = 1.0 - recovery
    # même logique d'interpolation linéaire
    t_mid = 0.5 * (t[:-1] + t[1:])
    df = np.exp(-risk_free_rate * t_mid)
    ee_mid = 0.5 * (EE[:-1] + EE[1:])

    # Base CVA, on reprend tout pour rester sur une fonction vextorisée
    base_lam = (base_cds_bps / 10000) / lgd
    base_mpd = np.diff(1.0 - np.exp(-base_lam * t))
    base_cva = float(np.sum(df * base_mpd * lgd * ee_mid))

    # Vectorised stressed CVAs: tout les CVA scenarios sont calculés en une fois
    lambdas = stressed_spreads / (10000 * lgd)
    # on fait attention au op vectorielles
    exp_t = np.exp(-lambdas[:, None] * t[None, :])
    marg_pd = np.diff(1.0 - exp_t, axis=1)
    stressed_cvas = np.sum(df * marg_pd * lgd * ee_mid, axis=1)

    delta_cva = stressed_cvas - base_cva

    var_95 = float(np.percentile(delta_cva, 95))
    var_99 = float(np.percentile(delta_cva, 99))

    mask = delta_cva >= var_99  # select les pires scenarios
    # expected shortfall, moyenne des pires scenarios
    es_99 = float(delta_cva[mask].mean()) if mask.any() else var_99

    return {
        "base_cva":          base_cva,
        "delta_cva":         delta_cva,
        "stressed_cvas":     stressed_cvas,
        "stressed_spreads":  stressed_spreads,
        "var_95":            var_95,
        "var_99":            var_99,
        "es_99":             es_99,
        "mean_delta":        float(delta_cva.mean()),
        "worst_delta":       float(delta_cva.max()),
        "mean_stressed_cva": float(stressed_cvas.mean())}
