import { useState } from 'react'
import { useEffect } from 'react';
import './PredictorPage.css'
import { abbr, logo } from '../constants/abbreviations';



function PredictorPage() {
    const [matches, setMatches] = useState([]);
    const [page, setPage] = useState(1);
    const [totalPages, setTotalPages] = useState(1);
    const [loading, setLoading] = useState(false);
    const [draftPage, setDraftPage] = useState(page);

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
            <div class="predictorpage-container">
                <h1>Predictions Tracker</h1>
                {loading ? (
                    <div style={{ textAlign: "center", minHeight: "600px" }}>
                        <span>Loading...</span>
                    </div>
                    ) : (
                        <table style={{ fontSize: "14px", margin: "0 auto" }}>
                            <thead>
                                <th>Sport</th>
                                <th>League</th>
                                <th>Date</th>
                                <th>Match</th>
                                <th>Score</th>
                                <th>Team 1 Line</th>
                                <th>Team 2 Line</th>
                                <th>Team 1 WP</th>
                                <th>Team 2 WP</th>
                                <th>Naive</th>
                                <th>Brier</th>
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
                                    <td></td>
                                    <td></td>
                                    <td></td>
                                    <td></td>
                                    <td></td>
                                    <td></td>
                                </tr>
                                ))}
                            </tbody>
                        </table>
                    )}
            </div>
        </>
    )
}

export default PredictorPage