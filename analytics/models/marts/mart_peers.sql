SELECT
    sel.ticker,                                  -- the selected company (relate this one)
    peer.ticker                       AS peer_ticker,
    peer.name                         AS peer_name,
    peer.industry                     AS peer_industry,
    peer.roic,
    peer.eps_cagr_3y,
    GREATEST(peer.free_cash_flow, 0)  AS fcf_bubble_size,
    sel.ticker = peer.ticker          AS is_selected
FROM {{ ref('int_kpis') }} AS sel
JOIN {{ ref('int_kpis') }} AS peer
    ON sel.sector = peer.sector