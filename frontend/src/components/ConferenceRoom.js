import React, { useState } from 'react';
import axios from 'axios';

const ConferenceRoom = ({ room }) => {
  const [votes, setVotes] = useState(room.votes);

  const vote = async () => {
    try {
      await axios.post('http://localhost:5000/api/vote', { room_id: room.id });
      setVotes(votes + 1);
    } catch (error) {
      alert(error.response.data.message);
    }
  };

  return (
    <tr>
      <td>{room.name}</td>
      <td>{votes}</td>
      <td>
        <button onClick={vote}>Vote</button>
      </td>
    </tr>
  );
};

export default ConferenceRoom;
