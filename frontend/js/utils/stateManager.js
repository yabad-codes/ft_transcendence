export function createState(initialState) {
	const updateMap = new Map();

	const handler = {
		set(target, key, value) {
		target[key] = value;
		const updateFunction = updateMap.get(key);
		if (updateFunction) {
			updateFunction();
		}
		return true;
		},
	};

	const state = new Proxy(initialState, handler);

	// Function to register a function to be called when a state changes
	function registerUpdate(key, updateFunction) {
		updateMap.set(key, updateFunction);
	}

	return { state, registerUpdate };
}
