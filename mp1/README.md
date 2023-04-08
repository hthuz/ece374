# ECE 428 MP1

## Message Data Format

Message ID:
`Sender's nodeID, Lamport Time`

Ask Message:  
`ASK | MessageID | MessageContent | Sender's Priority(turn/Lamport Time) | MulticastRequirement | Send Time`

Feedback Message:
`FEEDBACK | MessageID | Proposed Priority | Suggester? | MulticastRequirement | Send Time`

Decided Message:  
`DECIDED | MessageID | Agreed Priority | Suggested ID? | MulticastRequirement | Send Time`


Queue Element:  
`MessageContent | MessageID | Final Priority? | Deliverable | Sender's nodeID | [[Turn, Suggester's ID] [Turn Suggester's ID]] `
