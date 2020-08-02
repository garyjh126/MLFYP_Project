import React, {useState, useEffect} from 'react';
import '../styles/player.css';


function Player(props) {
    let which_player = props.is_ai? "player2": "player1";
    let tag = which_player==="player2"? "AI": "Guest";
    return (
        <div className={which_player}>
            <p className="playerTag">{tag}</p>
        </div>
    )
}

export default Player;
