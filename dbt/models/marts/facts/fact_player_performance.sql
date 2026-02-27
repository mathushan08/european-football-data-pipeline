{#
  MART MODEL: fact_player_performance
  Description: Fact table storing player performance metrics per competition per season.
  Grain: one player × one competition × one season
  Materialized as a partitioned and clustered table.
#}

WITH stg AS (

    SELECT * FROM {{ ref('stg_player_appearances') }}

),

ranked AS (

    SELECT
        *,

        -- ── Ranking: goal scorer rank within season + league ─────────────
        -- RANK() vs ROW_NUMBER(): RANK gives same rank for ties
        RANK() OVER (
            PARTITION BY season_year, competition_id
            ORDER BY total_goals DESC
        ) AS goal_scorer_rank,

        -- ── Ranking: assist leader rank ───────────────────────────────────
        RANK() OVER (
            PARTITION BY season_year, competition_id
            ORDER BY total_assists DESC
        ) AS assist_rank,

        -- ── Ranking: most minutes played ──────────────────────────────────
        RANK() OVER (
            PARTITION BY season_year, competition_id
            ORDER BY total_minutes DESC
        ) AS minutes_rank,

        -- ── Consistency score: high goals_per_90 + many appearances = reliable scorer
        -- Multiply by log to avoid overweighting players with 1 big game
        ROUND(
            goals_per_90 * LN(total_appearances + 1), 4
        ) AS scorer_consistency_score,

        -- ── Discipline rate: total cards per 90 minutes ───────────────────
        ROUND(
            SAFE_DIVIDE(
                (total_yellow_cards + total_red_cards * 2),   -- red = double weight
                total_minutes
            ) * 90, 4
        ) AS cards_per_90,

        -- ── Attacking efficiency: goal contributions per 90 ──────────────
        ROUND(
            SAFE_DIVIDE(total_goal_contributions, total_minutes) * 90, 4
        ) AS contributions_per_90

    FROM stg

)

SELECT
    -- ── Identity keys ────────────────────────────────────────────────────
    player_id,
    competition_id,
    league_name,
    country_name,
    season_year,
    season_label,

    -- ── Volume ────────────────────────────────────────────────────────────
    total_appearances,
    total_minutes,
    ROUND(avg_minutes_per_game, 1) AS avg_minutes_per_game,

    -- ── Goals & creativity ────────────────────────────────────────────────
    total_goals,
    total_assists,
    total_goal_contributions,

    -- ── Per-90 metrics ────────────────────────────────────────────────────
    goals_per_90,
    assists_per_90,
    contributions_per_90,

    -- ── Discipline ────────────────────────────────────────────────────────
    total_yellow_cards,
    total_red_cards,
    cards_per_90,

    -- ── Derived scores ────────────────────────────────────────────────────
    scorer_consistency_score,
    goal_contribution_rate,
    performance_tier,

    -- ── Rankings ──────────────────────────────────────────────────────────
    goal_scorer_rank,
    assist_rank,
    minutes_rank,

    -- ── Top-player flags ─────────────────────────────────────────────────
    (goal_scorer_rank <= 10)  AS is_top_10_scorer,
    (assist_rank <= 10)       AS is_top_10_assister

FROM ranked
