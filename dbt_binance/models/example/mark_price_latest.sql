{{ config(materialized='table') }}

WITH latest_price AS (
    SELECT
        symbol,
        MAX(event_time) AS max_event_time
    FROM mark_price
    GROUP BY symbol
)

SELECT
    mp.*,
    current_timestamp AS update_time
FROM mark_price AS mp
JOIN latest_price AS lp
    ON mp.symbol = lp.symbol
   AND mp.event_time = lp.max_event_time
