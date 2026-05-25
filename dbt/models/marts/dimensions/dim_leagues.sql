{#
  MART MODEL: dim_leagues
  Description: Dimension table storing all-time aggregated statistics and metadata for the top-5 European leagues.
#}

WITH league_stats AS (

    -- Aggregate league-level totals from staging
    SELECT
        competition_id,
        league_name,
        country_name,

        -- Season coverage
        MIN(season_year) AS first_season_year,
        MAX(season_year) AS last_season_year,
        COUNT(DISTINCT season_year) AS seasons_covered,

        -- Player pool
        COUNT(DISTINCT player_id) AS total_unique_players,

        -- History-wide scoring averages
        ROUND(AVG(goals_per_90),   3) AS avg_goals_per_90,
        ROUND(AVG(assists_per_90), 3) AS avg_assists_per_90,
        ROUND(AVG(avg_minutes_per_game), 1) AS avg_minutes_per_game,

        -- Discipline
        SUM(total_yellow_cards) AS all_time_yellow_cards,
        SUM(total_red_cards)    AS all_time_red_cards,
        ROUND(
            SAFE_DIVIDE(SUM(total_yellow_cards), COUNT(*)), 2
        ) AS avg_yellow_cards_per_player_season,

        -- Total goals scored across all seasons
        SUM(total_goals)   AS all_time_goals,
        SUM(total_assists) AS all_time_assists

    FROM {{ ref('stg_player_appearances') }}
    GROUP BY competition_id, league_name, country_name

),

with_metadata AS (

    SELECT
        competition_id,
        league_name,
        country_name,

        -- Map country (flag emoji removed)
        CASE competition_id
            WHEN 'GB1' THEN ''
            WHEN 'ES1' THEN ''
            WHEN 'L1'  THEN ''
            WHEN 'IT1' THEN ''
            WHEN 'FR1' THEN ''
        END AS country_flag,

        -- Display order for dashboards (UEFA ranking / prestige)
        CASE competition_id
            WHEN 'GB1' THEN 1
            WHEN 'ES1' THEN 2
            WHEN 'L1'  THEN 3
            WHEN 'IT1' THEN 4
            WHEN 'FR1' THEN 5
        END AS display_order,

        first_season_year,
        last_season_year,
        seasons_covered,
        total_unique_players,
        avg_goals_per_90,
        avg_assists_per_90,
        avg_minutes_per_game,
        all_time_yellow_cards,
        all_time_red_cards,
        avg_yellow_cards_per_player_season,
        all_time_goals,
        all_time_assists

    FROM league_stats

)

SELECT * FROM with_metadata
ORDER BY display_order
