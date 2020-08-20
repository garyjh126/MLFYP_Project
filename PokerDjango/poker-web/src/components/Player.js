import React, {useState, useEffect} from 'react';
import '../styles/player.css';
import Card from './Card.js'


function Player(props) {
    let which_player = props.is_ai? "player2": "player1";
    let tag = which_player==="player2"? "AI": "Guest";
    return (
        <div className={which_player}>
            <div className="holding">
                <Card value={'A'} suit={'d'}/>
                <Card value={'K'} suit={'s'}/>
            </div>
            

            <p className="playerTag">{tag}</p>
        </div>
    )
}

export default Player;
