async function predictGrowth() {
    const gender = document.getElementById('gender').value;
    const age = document.getElementById('age').value;
    const height = document.getElementById('height').value;
    const btn = document.querySelector('.btn-predict');
    
    const resultCol = document.getElementById('result-column');
    const resultBox = document.getElementById('result-box');
    const statusBadge = document.getElementById('status-badge');
    
    if(!age || !height) { alert("Please fill all fields!"); return; }

    btn.innerText = "Processing...";
    btn.disabled = true;

    try {
        const response = await fetch('/predict', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ gender, age, height })
        });
        const data = await response.json();

        resultCol.style.display = 'block';
        setTimeout(() => { resultCol.style.opacity = '1'; }, 50);

        document.getElementById('result-title').innerText = data.status;
        document.getElementById('ideal-msg').innerText = data.ideal_height_msg;
        document.getElementById('suggestion-intro').innerText = data.suggestion_intro;
        document.getElementById('status-badge').innerText = data.status;
        
        document.getElementById('food-name').innerText = data.food_name;
        document.getElementById('food-nutrition').innerText = data.food_nutrition;
        
        document.getElementById('food-img').src = "/static/Assets/" + data.food_image; 
        document.getElementById('food-img').onerror = function() {
            this.src = "https://placehold.co/400x200?text=" + data.food_name; // Fallback if image missing
        };

        document.getElementById('food-name').innerText = data.food_name;
        document.getElementById('food-nutrition').innerText = data.food_nutrition;
        document.getElementById('food-img').src = "/static/Assets/" + data.food_image;

        document.getElementById('btn-youtube').href = data.food_youtube;
        document.getElementById('btn-website').href = data.food_website;

        resultBox.className = 'custom-card result-card';
        statusBadge.className = 'status-badge';

        if (data.prediction_code === 0) { 
            resultBox.classList.add('border-normal');
            statusBadge.classList.add('bg-normal');
        } else if (data.prediction_code === 1) { 
            resultBox.classList.add('border-tall');
            statusBadge.classList.add('bg-tall');
        } else if (data.prediction_code === 2) { 
            resultBox.classList.add('border-stunted');
            statusBadge.classList.add('bg-stunted');
        } else { 
            resultBox.classList.add('border-severe');
            statusBadge.classList.add('bg-severe');
        }

    } catch (error) {
        console.error(error);
        alert("Error connecting to server.");
    } finally {
        btn.innerText = "Analyze Now";
        btn.disabled = false;
    }

    const data = await response.json();
}