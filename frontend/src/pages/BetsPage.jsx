import { useState } from 'react'
// import './App.css'
import './BetsPage.css'
import { useEffect } from 'react';
import { abbr, logo } from '../constants/abbreviations';


function BetsPage() {
    const [matches, setMatches] = useState([]);
    const [page, setPage] = useState(1);
    const [totalPages, setTotalPages] = useState(1);
    const [loading, setLoading] = useState(false);
    const [draftPage, setDraftPage] = useState(page);
    const [filterMenuActive, setFilterMenuActive] = useState(false);

    const commitPage = () => {
        const next = Math.min(Math.max(1, draftPage), totalPages);
        setPage(next);
    };

    useEffect(() => {
        setDraftPage(page);
    }, [page]);

    const getEVGradientStyle = (ev) => {
        const maxEV = 0.4; // EV at which green is "maxed out"
        const clampedEV = Math.min(ev, maxEV);
    
        // Normalize 0 → 1
        const intensity = clampedEV / maxEV;
    
        return {
        backgroundColor: `rgba(0, 180, 0, ${intensity})`,
        };
    };

    const getAVGradientStyle = (av) => {
        if (av < 0){
            return {
                backgroundColor: `rgba(120, 0, 0, 1)`,
            }
        } else {
            const maxAV = 1; // EV at which green is "maxed out"
            const clampedAV = Math.min(av, maxAV);
        
            // Normalize 0 → 1
            const intensity = clampedAV / maxAV;
        
            return {
            backgroundColor: `rgba(0, 180, 0, ${intensity})`,
            };
        }
    };

    useEffect(() => {
        // Call your backend API
        setLoading(true);

        fetch(`http://127.0.0.1:8000/api/matches?page=${page}&limit=50`)
        .then((res) => res.json())
        .then((data) => {
            setMatches(data.matches);
            setTotalPages(data.totalPages);
        })
        .catch((err) => console.error("Error fetching matches:", err))
        .finally(() => setLoading(false));
        
    }, [page]);

    return (
        <>
            <div class="betspage-container">
                <h1>Matches</h1>
                <div style={{ marginTop: "1rem", 
                                    marginBottom: "1rem", 
                                    position: "relative", 
                                    display: "inline-flex",
                                    alignItems: "center"}}>
                    <div onMouseEnter={() => setFilterMenuActive(true)}
                        onMouseLeave={() => setFilterMenuActive(false)}
                        style={{ position: "relative" }}>
                        <span 
                            style={{ padding: "0.5rem 1rem", cursor: "pointer" }}>
                            Filters
                        </span>

                        {filterMenuActive && (
                            <div
                                style={{
                                    position: "absolute",
                                    top: "100%",
                                    left: 0,
                                    padding: "1rem",
                                    background: "#000",
                                    border: "1px solid #ccc",
                                    borderRadius: "6px",
                                    boxShadow: "0 4px 12px rgba(0,0,0,0.1)",
                                    zIndex: 1000,
                                    minWidth: "200px"
                                }}
                            >
                                Leagues
                                <input type="checkbox" /> NBA
                                <input type="checkbox" /> NFL
                                <input type="checkbox" /> MLB
                                <input type="checkbox" /> NCAAF
                                <input type="checkbox" /> NCAAM
                            </div>
                        )}

                        <button
                            disabled={page === 1}
                            onClick={() => setPage(p => p - 1)}>
                            Prev
                        </button>

                        <span style={{ margin: "0 1rem" }}>
                            Page {page} of {totalPages}
                        </span>

                        <button
                            disabled={page === totalPages}
                            onClick={() => setPage(p => p + 1)}
                        >
                            Next
                        </button>



                        <span style={{ paddingLeft: "1rem", paddingRight: "1rem" }}>
                            Go to Page
                            <input
                                type="number"
                                value={draftPage}
                                min={1}
                                max={totalPages}
                                onChange={e => setDraftPage(Number(e.target.value))}
                                onKeyDown={e => {
                                if (e.key === "Enter") {
                                    commitPage();
                                }
                                }}
                                style={{ marginLeft: "1rem", marginRight: "1rem" }}
                            />

                            <button onClick={commitPage}>
                                Go
                            </button>
                        </span>
                    </div>
                </div>

                

                {loading ? (
                    <div style={{ textAlign: "center", minHeight: "600px" }}>
                        <span>Loading...</span>
                    </div>
                    ) : (
                        <table style={{ fontSize: "14px", margin: "0 auto" }}>
                            <thead>
                                <tr>
                                <th>Sport</th>
                                <th>League</th>
                                <th className="date-col">Date</th>
                                <th className="match-col">Match</th>
                                <th>Score</th>
                                <th className="bet-col">Bet</th>
                                <th>Line</th>
                                <th>Implied Odds</th>
                                <th>Win%</th>
                                <th>EV</th>
                                <th>EW</th>
                                <th>Result</th>
                                <th>Actual Value</th>
                                <th>Bookie</th>
                                </tr>
                            </thead>
                            <tbody>
                                {matches.map((match, index) => (
                                <tr>
                                    <td>{match.sport}</td>
                                    <td>{abbr(match.league)}</td>
                                    <td>{new Date(match.date).toLocaleString('en-US', {
                                        year: 'numeric',
                                        month: 'short',
                                        day: 'numeric',
                                        hour: '2-digit',
                                        minute: '2-digit',
                                        hour12: true
                                        })}
                                    </td>
                                    <td key={index}>
                                        <div className="team-cell">
                                            <img 
                                                src={logo(match.team_1)} 
                                                alt={''} 
                                                style={{ width: '20px', marginRight: '0.2rem' }}
                                            />
                                            {abbr(match.team_1)}
                                            {' vs '} 
                                            <img 
                                                src={logo(match.team_2)} 
                                                alt={''} 
                                                style={{ width: '20px', marginLeft: '0.3rem', marginRight: '0.2rem' }}
                                            />
                                            {abbr(match.team_2)}
                                        </div>
                                    </td>
                                    <td>{match.team_1_score}-{match.team_2_score}</td>
                                    <td>
                                        <div className="team-cell">
                                            <img 
                                                src={logo(match.bet['team'])} 
                                                alt={''} 
                                                style={{ width: '20px', marginRight: '0.2rem' }}
                                            />
                                            {abbr(match.bet['team'])}
                                        </div>
                                    </td>
                                    <td>{match.bet['line']}</td>
                                    <td>{isNaN(Number(match.bet.implied_odds)) ? '-' : Number(match.bet.implied_odds).toFixed(2)}</td>
                                    <td>{isNaN(Number(match.bet.winProb)) ? '-' : Number(match.bet.winProb).toFixed(2)}</td>
                                    <td style={getEVGradientStyle(match.bet.EV)}>
                                        {Number(match.bet['EV']).toFixed(3)}
                                    </td>
                                    <td>{Number(match.bet['EW']).toFixed(2)}</td>
                                    <td>{match.bet['result']}</td>
                                    <td style={getAVGradientStyle(match.bet.actual_value)}>
                                        {Number(match.bet['actual_value']).toFixed(2)}
                                    </td>
                                    <td>{match.bookmaker}</td>
                                </tr>
                                ))}
                            </tbody>
                        </table>
                    )}
            </div>
            <p>
                Created by Kevin Lim
            </p>
        </>
    )
}

export default BetsPage
