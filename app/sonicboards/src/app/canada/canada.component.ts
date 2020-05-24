import { Component, OnInit } from '@angular/core';
import { HttpClient } from "@angular/common/http";
import { trigger, style, animate, transition } from '@angular/animations';
import { environment } from 'src/environments/environment';

interface album {
  genre: string,
  region: string
}

@Component({
  selector: 'app-canada',
  templateUrl: './canada.component.html',
  styleUrls: ['./canada.component.css','../app.component.css'],
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
export class CanadaComponent implements OnInit {

  node_serve_url = '';
  current_tab = 'toronto';
  date_stamp_str = '';
  genre_flag = false; navbarOpen = false; allow_search = true;
  toronto_data = []; montreal_data = []; bc_data = []; prairies_data = [];
  ontario_data = []; quebec_data = []; atlantic_data = []; custom_data = [];

  // Dict storing the values of the custom region search buttons.
  sr_dict = {'sr-ab': true, 'sr-bc': true, 'sr-mn': true,
    'sr-nb': true, 'sr-nl': true, 'sr-ns': true, 'sr-on': true,
    'sr-pe': true, 'sr-qc': true, 'sr-sk': true}; sr_all_flag = true;

  // Dict storing the values of the custom genre search buttons.
  sg_dict = {'sg-ac': true, 'sg-al': true, 'sg-am': true, 'sg-bl': true,
    'sg-co': true, 'sg-el': true, 'sg-ex': true, 'sg-fo': true,
    'sg-fu': true, 'sg-hi': true, 'sg-ja': true, 'sg-po': true,
    'sg-pu': true, 'sg-rn': true, 'sg-re': true, 'sg-ro': true,
    'sg-so': true, 'sg-wo': true}; sg_all_flag = true;
  
  // region tag list
  BC_TAGS = ['britishcolumbia', 'vancouver', 'victoria'];
  PRAIRIE_TAGS = ['alberta', 'edmonton', 'calgary', 'saskatchewan', 'manitoba']
  ONTARIO_TAGS = ['toronto', 'ottawa', 'ontario']
  QUEBEC_TAGS = ['montreal', 'quebec']
  ATLANTIC_TAGS = ['newfoundland', 'novascotia', 'newbrunswick', 'pei']

  constructor(private httpClient: HttpClient) { }

  toggleNavbar() { this.navbarOpen = !this.navbarOpen; }

  // Toggle Genres button.
  onGenClick(event) {
    var text = event.target.textContent
    event.target.textContent = 
      (text == "Show Genres" ? "Hide Genres" : "Show Genres");
    this.genre_flag = !this.genre_flag;
    console.log(this.genre_flag)
  }

  // Select Category button.
  onCatClick(event) {
    if (event.target.id === "rb-to"){ this.current_tab = 'toronto' }
    else if (event.target.id === "rb-mo"){ this.current_tab = 'montreal' }
    else if (event.target.id === "rb-bc"){ this.current_tab = 'bc' }
    else if (event.target.id === "rb-pr"){ this.current_tab = 'prairies' }
    else if (event.target.id === "rb-on"){ this.current_tab = 'ontario' }
    else if (event.target.id === "rb-qu"){ this.current_tab = 'quebec' }
    else if (event.target.id === "rb-at"){ this.current_tab = 'atlantic' }
    else if (event.target.id === "rb-cs"){ this.current_tab = 'custom' }
  }

  onSrClick(event) {
    if(event.target.id === 'sr-all'){
      if(this.sr_all_flag){ 
        this.sr_all_flag = false; 
        Object.keys(this.sr_dict).forEach(function(index) {
          this.sr_dict[index] = false; }, this);
      } else { 
        this.sr_all_flag = true;
        Object.keys(this.sr_dict).forEach(function(index) {
          this.sr_dict[index] = true; }, this);
      }
    }else{
      this.sr_dict[event.target.id] = !this.sr_dict[event.target.id];
    }
  }

  onSgClick(event) {
    if(event.target.id === 'sg-all'){
      if(this.sg_all_flag){ 
        this.sg_all_flag = false; 
        Object.keys(this.sg_dict).forEach(function(index) {
          this.sg_dict[index] = false; }, this);
      } else { 
        this.sg_all_flag = true;
        Object.keys(this.sg_dict).forEach(function(index) {
          this.sg_dict[index] = true; }, this);
      }
    }else{
      this.sg_dict[event.target.id] = !this.sg_dict[event.target.id];
    }
  }

  // On Custom Search button. Prevent rapid button clicks.
  onSeaClick(event) {
    if (this.allow_search){

      // Create an array which stores the genres to query based on buttons.
      var genres_to_query = []
      if(this.sg_dict['sg-ac']) { genres_to_query.push('acoustic') }
      if(this.sg_dict['sg-al']) { genres_to_query.push('alternative') }
      if(this.sg_dict['sg-am']) { genres_to_query.push('ambient') }
      if(this.sg_dict['sg-bl']) { genres_to_query.push('blues') }
      if(this.sg_dict['sg-co']) { genres_to_query.push('country') }
      if(this.sg_dict['sg-el']) { genres_to_query.push('electronic') }
      if(this.sg_dict['sg-ex']) { genres_to_query.push('experimental') }
      if(this.sg_dict['sg-fo']) { genres_to_query.push('folk') }
      if(this.sg_dict['sg-fu']) { genres_to_query.push('funk') }
      if(this.sg_dict['sg-hi']) { genres_to_query.push('hip-hop/rap') }
      if(this.sg_dict['sg-ja']) { genres_to_query.push('jazz') }
      if(this.sg_dict['sg-po']) { genres_to_query.push('pop') }
      if(this.sg_dict['sg-pu']) { genres_to_query.push('punk') }
      if(this.sg_dict['sg-rn']) { genres_to_query.push('r&b/soul') }
      if(this.sg_dict['sg-re']) { genres_to_query.push('reggae') }
      if(this.sg_dict['sg-ro']) { genres_to_query.push('rock') }
      if(this.sg_dict['sg-so']) { genres_to_query.push('soundtrack') }
      if(this.sg_dict['sg-wo']) { genres_to_query.push('world') }

      // Create an array which stores the regions to query based on buttons.
      var regions_to_query = []
      if(this.sr_dict['sr-ab']) { 
        regions_to_query.push('alberta', 'calgary', 'edmonton') }
      if(this.sr_dict['sr-bc']) { 
        regions_to_query.push('britishcolumbia', 'vancouver', 'victoria') }
      if(this.sr_dict['sr-mn']) { regions_to_query.push('manitoba') }
      if(this.sr_dict['sr-nb']) { regions_to_query.push('newbrunswick') }
      if(this.sr_dict['sr-nl']) { regions_to_query.push('newfoundland') }
      if(this.sr_dict['sr-ns']) { regions_to_query.push('novascotia') }
      if(this.sr_dict['sr-on']) { 
        regions_to_query.push('ontario', 'toronto', 'ottawa') }
      if(this.sr_dict['sr-pe']) { regions_to_query.push('pei') }
      if(this.sr_dict['sr-qc']) { 
        regions_to_query.push('quebec', 'montreal') }
      if(this.sr_dict['sr-sk']) { regions_to_query.push('saskatchewan') }

      this.httpClient
      .post(this.node_serve_url + '/api/canada', { 
        genres: genres_to_query, regions: regions_to_query})
      .subscribe((data : Array<Object>)=> { this.custom_data = data })

      this.allow_search = false
      setTimeout(() => { this.allow_search = true }, 2000)
    }
  }

  ngOnInit(): void {
    // Setup backend connection. Https connection if in production mode.
    if(environment.production){
      this.node_serve_url = "https://sonicboards.com:3000"
    }else{ this.node_serve_url = "http://localhost:3000" }
    
    this.httpClient
    .post(this.node_serve_url + '/api/canada', {regions: ['toronto']})
    .subscribe((data : Array<Object>)=> { 
      this.preloadImages(data); this.toronto_data = data })

    this.httpClient
    .post(this.node_serve_url + '/api/canada', {regions: ['montreal']})
    .subscribe((data : Array<Object>)=> { 
      this.preloadImages(data); this.montreal_data = data })

    this.httpClient
    .post(this.node_serve_url + '/api/canada', {regions: this.BC_TAGS})
    .subscribe((data : Array<Object>)=> { 
      this.preloadImages(data); this.bc_data = data })

    this.httpClient
    .post(this.node_serve_url + '/api/canada', {regions: this.PRAIRIE_TAGS})
    .subscribe((data : Array<Object>)=> { 
      this.preloadImages(data); this.prairies_data = data })

    this.httpClient
    .post(this.node_serve_url + '/api/canada', {regions: this.ONTARIO_TAGS})
    .subscribe((data : Array<Object>)=> { 
      this.preloadImages(data); this.ontario_data = data })
    
    this.httpClient
    .post(this.node_serve_url + '/api/canada', {regions: this.QUEBEC_TAGS})
    .subscribe((data : Array<Object>)=> { 
      this.preloadImages(data); this.quebec_data = data })

    this.httpClient
    .post(this.node_serve_url + '/api/canada', {regions: this.ATLANTIC_TAGS})
    .subscribe((data : Array<Object>)=> { 
      this.preloadImages(data); this.atlantic_data = data })

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
