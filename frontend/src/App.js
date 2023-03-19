import React, { useState, useEffect } from 'react';
import axios from 'axios';
import ConferenceRoom from './components/ConferenceRoom';

const App = () => {
  const [conferenceRooms, setConferenceRooms] = useState([]);
  const [newRoomName, setNewRoomName] = useState('');

  useEffect(() => {
    const fetchConferenceRooms = async () => {
      const response = await axios.get('http://localhost:5000/api/conference_rooms');
      setConferenceRooms(response.data);
    };

    fetchConferenceRooms();
  }, []);

  const addConferenceRoom = async () => {
    try {
      const response = await axios.post('http://localhost:5000/api/conference_rooms', { name: newRoomName });
      setConferenceRooms([...conferenceRooms, response.data]);
      setNewRoomName('');
    } catch (error) {
      alert(error.response.data.message);
    }
  };

  return (
    <div className="App">
      <h1>Conference Room Voting</h1>
      <input
        type="text"
        value={newRoomName}
        onChange={(e) => setNewRoomName(e.target.value)}
        placeholder="Conference room name"
      />
      <button onClick={addConferenceRoom}>Save</button>
      <table>
        <thead>
          <tr>
            <th>Name</th>
            <th>Votes</th>
            <th>Action</th>
          </tr>
        </thead>
        <tbody>
          {conferenceRooms.map((room) => (
            <ConferenceRoom key={room.id} room={room} />
          ))}
        </tbody>
      </table>
    </div>
  );
};

export default App;
