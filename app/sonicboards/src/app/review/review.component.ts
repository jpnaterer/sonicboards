import { Component, OnInit } from '@angular/core';
import { HttpClient } from "@angular/common/http";
import { trigger, style, animate, transition } from '@angular/animations';
import { environment } from 'src/environments/environment';

@Component({
  selector: 'app-review',
  templateUrl: './review.component.html',
  styleUrls: ['./review.component.css','../app.component.css'],
  animations: [
    trigger(
      'genreToggle', [
        transition(':enter', [
          style({transform: 'translateX(100%)', opacity: 0}),
          animate('400ms', style({transform: 'translateX(0%)', opacity: 1}))
        ]),
        transition(':leave', [
          style({transform: 'translateX(0%)', opacity: 1}),
          animate('400ms', style({transform: 'translateX(100%)', opacity: 0}))
        ])
      ]
    )
  ]
})
export class ReviewComponent implements OnInit {

  node_serve_url = '';
  current_tab = '';
  date_stamp_str = '';
  genre_flag = false;
  navbarOpen = false;
  pitchfork_data = [];
  allmusic_data = [];

  constructor(private httpClient: HttpClient){}

  // Toggle Genres button.
  onGenClick(event) {
    var text = event.target.textContent
    event.target.textContent = 
      (text == "Show Genres" ? "Hide Genres" : "Show Genres");
    this.genre_flag = !this.genre_flag;
  }
  
  // Select Category button.
  onCatClick(event) {
    if (event.target.id === "rb-pf"){
      this.current_tab = 'pitchfork';
    }else if (event.target.id === "rb-am"){
      this.current_tab = 'allmusic';
    }
  }

  ngOnInit(){
    // Setup backend connection. Https connection if in production mode.
    if(environment.production){
      this.node_serve_url = "https://sonicboards.com:3000"
    }else{ this.node_serve_url = "http://localhost:3000" }

    this.httpClient
    .post(this.node_serve_url + '/api/reviews', 
      [{source: 'pitchfork'}, {source: 'allmusic'}])
    .subscribe((data : Array<Array<Object>>)=> { 
      this.preloadImages([].concat.apply([], data)); 
      this.pitchfork_data = data[0];
      this.allmusic_data = data[1];
      this.current_tab = 'pitchfork';
    })

    this.httpClient
    .post(this.node_serve_url + '/api/config', {})
    .subscribe((data : string)=> { 
      var w = new Date(data)
      var d = w.getDate() < 10 ? '0' + w.getDate() : w.getDate()
      var m = w.getMonth() < 9 ? '0' + (w.getMonth()+1) : (w.getMonth()+1)
      this.date_stamp_str = `${m}-${d}-${w.getFullYear()}`
    })
  }

  preloadImages(api_data) {
    var images = []
    for (var i = 0; i < api_data.length; i++) {
      images[i] = new Image();
      images[i].src = api_data[i]['sp_img'];
    }
  }

}
