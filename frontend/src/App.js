import React, { useState, useEffect } from 'react';
import axios from 'axios';
import ConferenceRoom from './components/ConferenceRoom';
import './App.css';

const App = () => {
  const [conferenceRooms, setConferenceRooms] = useState([]);
  const [newRoomName, setNewRoomName] = useState('');
  const [newRoomDescription, setNewRoomDescription] = useState('');

  useEffect(() => {
    const fetchConferenceRooms = async () => {
      const response = await axios.get('http://192.168.50.45:5000/api/conference_rooms');
      setConferenceRooms(response.data);
    };

    fetchConferenceRooms();
  }, []);

  const addConferenceRoom = async () => {
    try {
      const response = await axios.post('http://192.168.50.45:5000/api/conference_rooms', { name: newRoomName, description: newRoomDescription });
      setConferenceRooms([...conferenceRooms, response.data]);
      setNewRoomName('');
      setNewRoomDescription('');
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
      <input
          type="text"
          placeholder="Conference room description"
          value={newRoomDescription}
          onChange={(e) => setNewRoomDescription(e.target.value)}
        />
      <button onClick={addConferenceRoom}  disabled={!newRoomName.trim()}>Save</button>
      <table>
        <thead>
          <tr>
            <th>Name</th>
            <th>Description</th>
            <th>Votes</th>
            <th>Action</th>
          </tr>
        </thead>
        <tbody>
          {conferenceRooms
          .sort((a, b) => b.votes - a.votes)
          .map((room) => (
            <ConferenceRoom key={room.id} room={room} />
          ))}
        </tbody>
      </table>
    </div>
  );
};

export default App;
