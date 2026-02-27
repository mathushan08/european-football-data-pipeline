{#
  STAGING MODEL: stg_player_appearances
  Description: Staging model to clean, cast, and prepare raw player season stats.
#}

WITH source AS (

    SELECT * FROM {{ source('raw_football', 'player_season_stats') }}

),

renamed AS (

    SELECT
        -- ── Identity ──────────────────────────────────────────────────────
        CAST(player_id    AS INT64)   AS player_id,
        CAST(competition_id AS STRING) AS competition_id,
        CAST(league_name   AS STRING) AS league_name,
        CAST(country_name  AS STRING) AS country_name,
        CAST(season_year   AS INT64)  AS season_year,

        -- ── Volume metrics ────────────────────────────────────────────────
        CAST(total_appearances AS INT64) AS total_appearances,
        CAST(total_minutes     AS INT64) AS total_minutes,
        CAST(avg_minutes_per_game AS FLOAT64) AS avg_minutes_per_game,

        -- ── Attacking metrics ─────────────────────────────────────────────
        CAST(total_goals             AS INT64)   AS total_goals,
        CAST(total_assists           AS INT64)   AS total_assists,
        CAST(total_goal_contributions AS INT64)  AS total_goal_contributions,

        -- ── Per-90 minute metrics ─────────────────────────────────────────
        CAST(goals_per_90   AS FLOAT64) AS goals_per_90,
        CAST(assists_per_90 AS FLOAT64) AS assists_per_90,

        -- ── Discipline metrics ────────────────────────────────────────────
        CAST(total_yellow_cards AS INT64) AS total_yellow_cards,
        CAST(total_red_cards    AS INT64) AS total_red_cards,

        -- ── Labels ───────────────────────────────────────────────────────
        CAST(performance_tier AS STRING) AS performance_tier,

        -- ── Derived: season label (e.g. "2023/24") ────────────────────────
        CONCAT(
            CAST(season_year      AS STRING), '/',
            CAST(season_year + 1  AS STRING)
        ) AS season_label,

        -- ── Derived: goal_contribution_rate ──────────────────────────────
        -- What % of appearances resulted in a goal or assist?
        SAFE_DIVIDE(total_goal_contributions, total_appearances) AS goal_contribution_rate

    FROM source

    -- Filter: must have played at least 1 official appearance
    WHERE total_appearances > 0

)

SELECT * FROM renamed
